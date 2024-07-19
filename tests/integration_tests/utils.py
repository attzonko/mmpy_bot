import time
from multiprocessing import Process
from typing import Dict

import pytest
from filelock import FileLock

from mmpy_bot import (
    Bot,
    ExamplePlugin,
    Message,
    Plugin,
    Settings,
    WebHookExample,
    listen_to,
)
from mmpy_bot.driver import Driver

OFF_TOPIC_ID = "ahzqezf33jny9mpst758dnaahw"  # Channel id
TEAM_ID = "h6aje7ujgpggjrtik6f3m8fjah"
MAIN_BOT_ID = "hjawadm1ntdxzefd193x8mos7a"
RESPONSE_TIMEOUT = 15


def expect_reply(driver: Driver, post: Dict, wait=RESPONSE_TIMEOUT, retries=1):
    """Utility function to specify we expect some kind of reply after `wait` seconds."""
    reply = None
    for _ in range(retries + 1):
        time.sleep(wait)
        thread_info = driver.get_post_thread(post["id"])
        print(thread_info)
        reply_id = thread_info["order"][-1]
        if reply_id != post["id"]:
            reply = thread_info["posts"][reply_id]
            break

    if reply is None:
        raise ValueError("Expected a response, but didn't get any!")

    return reply


class TestPlugin(Plugin):
    @listen_to("^starting integration tests")
    async def reply_start(self, message: Message):
        self.driver.reply_to(message, "Bring it on!")


# For direct message tests
class DirectPlugin(Plugin):
    @listen_to("^starting direct tests")
    async def reply_start_direct(self, message: Message):
        self.driver.reply_to(message, "Bring direct on!")

    @listen_to("^direct reply (.*)")
    async def reply_direct(self, message: Message, text):
        self.driver.reply_to(message, f"Telling you privately! {text}", direct=True)


@pytest.fixture(scope="session")
def driver():
    return Bot(
        settings=Settings(
            MATTERMOST_URL="http://127.0.0.1",
            BOT_TOKEN="7arqwr6kzibc58zomct9ndfk1e",
            MATTERMOST_PORT=8065,
            SSL_VERIFY=False,
            WEBHOOK_HOST_ENABLED=True,
            WEBHOOK_HOST_URL="http://127.0.0.1",
            WEBHOOK_HOST_PORT=8579,
        ),
        plugins=[],  # We only use this to send messages, not to reply to anything.
    ).driver


# At the start of the pytest session, the bot is started
@pytest.fixture(scope="session", autouse=True)
def start_bot(request):
    lock = FileLock("./bot.lock")

    try:
        # We want to run the tests in multiple parallel processes, but launch at most
        # a single bot.
        lock.acquire(timeout=0.01)
        bot = Bot(
            settings=Settings(
                MATTERMOST_URL="http://127.0.0.1",
                BOT_TOKEN="e691u15hajdebcnqpfdceqihcc",
                MATTERMOST_PORT=8065,
                SSL_VERIFY=False,
                WEBHOOK_HOST_ENABLED=True,
                WEBHOOK_HOST_URL="http://127.0.0.1",
                WEBHOOK_HOST_PORT=8579,
            ),
            plugins=[DirectPlugin(), TestPlugin(), ExamplePlugin(), WebHookExample()],
        )

        def run_bot():
            bot.run()

        # Start the bot now
        bot_process = Process(target=run_bot)
        bot_process.start()

        def stop_bot():
            time.sleep(5)
            bot_process.terminate()
            lock.release()

        # Once all tests are finished, stop the bot
        request.addfinalizer(stop_bot)

    except TimeoutError:
        # If the lock times out, it means a bot is already running and we don't need
        # to do anything here.
        pass

    finally:
        time.sleep(5)  # Give the bot some time to start up
