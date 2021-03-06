import time

from .utils import start_bot  # noqa, only imported so that the bot is started
from .utils import MAIN_BOT_ID, OFF_TOPIC_ID, RESPONSE_TIMEOUT, TEAM_ID
from .utils import driver as driver_fixture
from .utils import expect_reply

# Hacky workaround to import the fixture without linting errors
driver = driver_fixture


# Verifies that the bot is running and listening to this non-targeted message
def test_start(driver):
    post = driver.create_post(OFF_TOPIC_ID, "starting integration tests!")
    assert expect_reply(driver, post)["message"] == "Bring it on!"


class TestExamplePlugin:
    def test_sleep(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "@main_bot sleep 5")
        # wait at least 10 seconds
        reply = expect_reply(driver, post, wait=max(10, RESPONSE_TIMEOUT), retries=0)
        assert reply["message"] == "Done!"
        # At least 5 seconds must have passed between our message and the response
        assert reply["create_at"] - post["create_at"] >= 5000

    def test_admin(self, driver):
        # Since this is not a direct message, we expect no reply at all
        post_id = driver.create_post(OFF_TOPIC_ID, "@main_bot admin")["id"]
        time.sleep(RESPONSE_TIMEOUT)
        thread_info = driver.get_thread(post_id)
        assert len(thread_info["order"]) == 1

        # For the direct message, we expect to have insufficient permissions, since
        # our name isn't admin
        private_channel = driver.channels.create_direct_message_channel(
            [driver.user_id, MAIN_BOT_ID]
        )["id"]
        post = driver.create_post(private_channel, "admin")
        reply = expect_reply(driver, post)
        assert reply["message"] == "You do not have permission to perform this action!"

    def test_hello_click(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "@main_bot hello_click arg1")
        reply = expect_reply(driver, post)
        assert reply["message"] == (
            "Received the following arguments:\n"
            "- positional_arg: arg1\n"
            "- keyword_arg: 5.0\n"
            "- flag: False\n"
        )
        post = driver.create_post(
            OFF_TOPIC_ID, "@main_bot hello_click arg2 -f --keyword-arg=7"
        )
        reply = expect_reply(driver, post)
        assert reply["message"] == (
            "Received the following arguments:\n"
            "- positional_arg: arg2\n"
            "- keyword_arg: 7.0\n"
            "- flag: True\n"
        )

    def test_hello_channel(self, driver):
        original_post = driver.create_post(OFF_TOPIC_ID, "@main_bot hello_channel")
        time.sleep(RESPONSE_TIMEOUT)

        as_expected = False
        for id, post in driver.posts.get_posts_for_channel(OFF_TOPIC_ID)[
            "posts"
        ].items():
            if (
                post["message"] == "hello channel!"
                and post["create_at"] > original_post["create_at"]
            ):
                as_expected = True
                break
        if not as_expected:
            raise ValueError(
                "Expected bot to reply 'hello channel!', but found no such message!"
            )

    def test_hello_ephemeral(self, driver):
        """Unfortunately ephemeral posts do not show up through the thread API, so we
        cannot check if an ephemeral reply was sent successfully.

        We can only check whether the right response is sent in case the bot doesn't
        have permission to send ephemeral posts.
        """
        post = driver.create_post(OFF_TOPIC_ID, "@main_bot hello_ephemeral")
        reply = expect_reply(driver, post)
        assert reply["message"] == "I do not have permission to create ephemeral posts!"

    def test_react(self, driver):
        post_id = driver.create_post(OFF_TOPIC_ID, "@main_bot hello_react")["id"]
        time.sleep(RESPONSE_TIMEOUT)
        reactions = driver.reactions.get_reactions_of_post(post_id)
        assert len(reactions) == 1
        assert reactions[0]["emoji_name"] == "+1"

    def test_file(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "@main_bot hello_file")
        reply = expect_reply(driver, post)
        assert len(reply["metadata"]["files"]) == 1
        file = reply["metadata"]["files"][0]
        assert file["name"] == "hello.txt"
        file = driver.files.get_file(file["id"])
        assert file.content.decode("utf-8") == "Hello from this file!"

    def test_trigger_webhook(self, driver):
        original_post = driver.create_post(OFF_TOPIC_ID, "!hello_webhook")
        time.sleep(RESPONSE_TIMEOUT)

        message = None
        for post in driver.posts.get_posts_for_channel(OFF_TOPIC_ID)["posts"].values():
            if (
                post["message"].lower() == "hello?"
                and post["create_at"] > original_post["create_at"]
            ):
                message = post
                break

        if not message:
            raise ValueError(
                "Expected bot to reply 'Hello?', but found no such message!"
            )

        assert message["props"]["from_webhook"] == "true"
        assert message["props"]["webhook_display_name"] == "TestHook"
        assert len(message["props"]["attachments"]) == 1

        attachment = message["props"]["attachments"][0]
        assert attachment["author_name"] == "Author"
        assert attachment["title"] == "Title"
        assert attachment["text"] == "Attachment text here..."

    def test_info(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "!info")
        user_info = driver.get_user_info(driver.user_id)

        reply = expect_reply(driver, post)["message"]
        reply = {
            line.split(": ")[0].lower(): line.split(": ")[1]
            for line in reply.split("\n")
        }
        assert reply["team-id"] == TEAM_ID
        assert reply["username"] == driver.username
        assert reply["email"] == user_info["email"]
        assert reply["user-id"] == driver.user_id
        assert reply["is-direct"] == "False"
        assert reply["mentions"] == "[]"
        assert reply["message"] == "!info"

    def test_ping(self, driver):
        post = driver.create_post(OFF_TOPIC_ID, "@main_bot ping")
        assert expect_reply(driver, post)["message"] == "pong"
