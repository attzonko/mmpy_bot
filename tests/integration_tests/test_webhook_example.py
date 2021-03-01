import asyncio
import time

from .utils import start_bot  # noqa, only imported so that the bot is started
from .utils import OFF_TOPIC_ID, RESPONSE_TIMEOUT
from .utils import driver as driver_fixture
from .utils import expect_reply

# Hacky workaround to import the fixture without linting errors
driver = driver_fixture


class TestWebHookExample:
    def test_webhook_listener(self, driver):
        asyncio.run(driver.trigger_own_webhook("ping", {"channel_id": OFF_TOPIC_ID}))
        time.sleep(RESPONSE_TIMEOUT)

        as_expected = False
        for post in driver.posts.get_posts_for_channel(OFF_TOPIC_ID)["posts"].values():
            # TODO: Check that the post was created after we triggered the webhook.
            # That isn't trivial due to potential timezone differences etc.
            if post["message"] == "Webhook ping triggered!":
                as_expected = True
                break
        if not as_expected:
            raise ValueError(
                "Expected bot to post 'Webhook ping triggered!', but found no such message!"
            )

    def test_button(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "!button")
        reply = expect_reply(driver, post, retries=2)
        assert len(reply["props"]["attachments"]) == 1
        attachment = reply["props"]["attachments"][0]
        assert attachment["actions"] == [
            {"id": "sendPing", "name": "Ping"},
            {"id": "sendPong", "name": "Pong"},
        ]
