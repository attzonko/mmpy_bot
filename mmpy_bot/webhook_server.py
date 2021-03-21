import asyncio
import random
import time
from queue import Empty, Queue
from typing import Optional

from aiohttp import web

from mmpy_bot.wrappers import ActionEvent, WebHookEvent


class NoResponse:
    """Used to notify the request handler that no web response should be sent."""

    pass


def handle_json_error(func):
    async def handler(instance, request: web.Request):
        try:
            return await func(instance, request)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            return web.json_response({"status": "failed", "reason": str(e)}, status=400)

    return handler


class WebHookServer:
    """A small server that listens to incoming webhooks and forwards them to the bot
    EventHandler in the main thread/process."""

    def __init__(
        self,
        url: str,
        port: int,
        event_queue: Optional[Queue] = None,
        response_queue: Optional[Queue] = None,
    ):
        self.app = web.Application()
        self.app_runner = web.AppRunner(self.app)
        self.url = url
        self.port = port
        self.running = False

        # Create queues if necessary.
        self.event_queue = event_queue or Queue()
        self.response_queue = response_queue or Queue()
        self.response_handlers = {}

        # Register /hooks endpoint
        self.app.add_routes([web.post("/hooks/{webhook_id}", self.process_webhook)])

    async def start(self):
        webhook_host_ip = self.url.replace("http://", "")
        await self.app_runner.setup()
        site = web.TCPSite(self.app_runner, webhook_host_ip, self.port)
        await site.start()
        self.running = True

        # Schedule the response awaiting function to the same loop as the web server
        asyncio.get_event_loop().create_task(self._obtain_responses_loop())

    async def stop(self):
        await self.app_runner.cleanup()
        self.running = False

    async def _obtain_responses_loop(self):
        """Checks the response queue for incoming responses and passes them on to the
        functions awaiting them."""
        while True:
            try:
                request_id, response = self.response_queue.get_nowait()
                print(f"Received response {response} for request {request_id}")
                try:
                    if not self.response_handlers[request_id].cancelled():
                        self.response_handlers[request_id].set_result(response)
                    del self.response_handlers[request_id]
                except KeyError:
                    # If this handler already received a response, we can skip this.
                    pass
            except Empty:
                pass
            await asyncio.sleep(0.0001)

    @handle_json_error
    async def process_webhook(self, request: web.Request):
        data = await request.json()
        webhook_id = request.match_info.get("webhook_id", "")
        if "trigger_id" in data:
            # Use the trigger ID to identify this request
            event = ActionEvent(
                data, request_id=data["trigger_id"], webhook_id=webhook_id
            )
        else:
            # Generate an ID based on the current time and a random number.
            event = WebHookEvent(
                data,
                request_id=f"{time.time()}_{random.randint(0, 10000)}",
                webhook_id=webhook_id,
            )
        self.event_queue.put(event)

        # Register a Future object that will signal us when a response has arrived,
        # and wait for it to complete.
        await_response = asyncio.get_event_loop().create_future()
        self.response_handlers[event.request_id] = await_response
        await await_response

        result = await_response.result()
        if result is NoResponse:
            return web.Response(status=200)

        return web.json_response(result)
