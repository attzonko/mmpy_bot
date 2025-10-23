import asyncio
import threading
import time

import pytest
from aiohttp import ClientSession

from mmpy_bot import Settings
from mmpy_bot.threadpool import ThreadPool
from mmpy_bot.webhook_server import NoResponse, WebHookServer


@pytest.fixture(scope="function")
def threadpool():
    pool = ThreadPool(num_workers=1)
    yield pool
    pool.stop()  # if the pool was started, stop it.


class TestWebHookServer:
    def test_start(self, threadpool):
        # Test server startup with a different port so it won't clash with the
        # integration tests
        server = WebHookServer(port=3281, url=Settings().WEBHOOK_HOST_URL)
        threadpool.start_webhook_server_thread(server)
        threadpool.start()
        time.sleep(1)
        assert server.running

        asyncio.set_event_loop(asyncio.new_event_loop())

        # Run the other tests sequentially
        self.test_obtain_response(server)
        self.test_process_webhook(server)

        # Test shutdown procedure
        threadpool.stop()
        assert not server.running

    @pytest.mark.skip("Called from test_start since we can't parallellize this.")
    def test_obtain_response(self, server):
        assert server.response_handlers == {}
        # Wait for a response for request id 'test
        await_response = asyncio.get_event_loop().create_future()
        server.response_handlers["test"] = await_response
        assert not server.response_handlers["test"].done()

        # We have no futures waiting for request id 'nonexistent', so nothing should
        # happen.
        server.response_queue.put(("nonexistent", None))
        time.sleep(1)
        assert not server.response_handlers["test"].done()

        # If a response comes in for request id 'test', it should be removed from the
        # response handlers dict.
        server.response_queue.put(("test", None))
        time.sleep(1)
        assert "test" not in server.response_handlers

    @pytest.mark.skip("Called from test_start since we can't parallellize this.")
    def test_process_webhook(self, server):
        """Checks whether an incoming webhook post request is correctly handled."""
        assert server.event_queue.empty()
        assert server.response_queue.empty()
        assert server.response_handlers == {}

        async def send_request(data):
            async with ClientSession() as session:
                try:
                    response = await session.post(
                        f"{server.url}:{server.port}/hooks/test_hook",
                        json=data,
                        timeout=1,
                    )
                    return await response.json()
                except asyncio.exceptions.TimeoutError:
                    return None

        asyncio.run(send_request({"text": "Hello!"}))
        # Verify that a WebHookEvent corresponding to our request was added to the
        # event queue.
        assert server.event_queue.qsize() == 1
        event = server.event_queue.get_nowait()
        assert event.webhook_id == "test_hook"
        assert event.text == "Hello!"

        # Since there is no MessageHandler, we have to signal the server ourselves
        server.response_queue.put((event.request_id, NoResponse))
        time.sleep(1)
        # Upon receiving the NoResponse, the server should have emptied the response
        # queue and handlers.
        assert server.response_queue.empty()
        assert server.response_handlers == {}

        # Test whether the web response is correctly passed through, if there is one
        response = {"text": "test response"}

        def provide_response():
            event = server.event_queue.get()
            server.response_queue.put((event.request_id, response))

        thread = threading.Thread(target=provide_response)
        thread.start()
        assert asyncio.run(send_request({"text": "Hello!"})) == response
