import asyncio
import json
from unittest import mock

from mmpy_bot import ExamplePlugin, Message, Settings, WebHookExample
from mmpy_bot.driver import Driver
from mmpy_bot.event_handler import EventHandler
from mmpy_bot.plugins import PluginManager
from mmpy_bot.wrappers import WebHookEvent


def create_message(
    text="hello",
    mentions=["qmw86q7qsjriura9jos75i4why"],
    channel_type="O",
    sender_name="betty",
):
    return Message(
        {
            "event": "posted",
            "data": {
                "channel_display_name": "Off-Topic",
                "channel_name": "off-topic",
                "channel_type": channel_type,
                "mentions": mentions,
                "post": {
                    "id": "wqpuawcw3iym3pq63s5xi1776r",
                    "create_at": 1533085458236,
                    "update_at": 1533085458236,
                    "edit_at": 0,
                    "delete_at": 0,
                    "is_pinned": "False",
                    "user_id": "131gkd5thbdxiq141b3514bgjh",
                    "channel_id": "4fgt3n51f7ftpff91gk1iy1zow",
                    "root_id": "",
                    "parent_id": "",
                    "original_id": "",
                    "message": text,
                    "type": "",
                    "props": {},
                    "hashtags": "",
                    "pending_post_id": "",
                },
                "sender_name": sender_name,
                "team_id": "au64gza3iint3r31e7ewbrrasw",
            },
            "broadcast": {
                "omit_users": "None",
                "user_id": "",
                "channel_id": "4fgt3n51f7ftpff91gk1iy1zow",
                "team_id": "",
            },
            "seq": 29,
        }
    )


class TestEventHandler:
    @mock.patch("mmpy_bot.driver.Driver.username", new="my_username")
    def test_init(self):
        handler = EventHandler(
            Driver(),
            Settings(),
            plugins=PluginManager([ExamplePlugin(), WebHookExample()]),
        )
        # Test the name matcher regexp
        assert handler._name_matcher.match("@my_username are you there?")
        assert not handler._name_matcher.match("@other_username are you there?")

        # Test that all listeners from the individual plugins are now registered on
        # the handler
        for plugin in handler.plug_manager:
            for pattern, listener in plugin.message_listeners.items():
                assert listener in handler.message_listeners[pattern]
            for pattern, listener in plugin.webhook_listeners.items():
                assert listener in handler.webhook_listeners[pattern]

        # And vice versa, check that any listeners on the handler come from the
        # registered plugins
        for pattern, listeners in handler.message_listeners.items():
            for listener in listeners:
                assert any(
                    [
                        pattern in plugin.message_listeners
                        and listener in plugin.message_listeners[pattern]
                        for plugin in handler.plug_manager
                    ]
                )
        for pattern, listeners in handler.webhook_listeners.items():
            for listener in listeners:
                assert any(
                    [
                        pattern in plugin.webhook_listeners
                        and listener in plugin.webhook_listeners[pattern]
                        for plugin in handler.plug_manager
                    ]
                )

    @mock.patch("mmpy_bot.driver.Driver.username", new="my_username")
    def test_should_ignore(self):
        handler = EventHandler(
            Driver(), Settings(IGNORE_USERS=["ignore_me"]), plugins=PluginManager([])
        )
        # We shouldn't ignore a message from betty, since she is not listed
        assert not handler._should_ignore(create_message(sender_name="betty"))
        assert handler._should_ignore(create_message(sender_name="ignore_me"))

        # We ignore our own messages by default
        assert handler._should_ignore(create_message(sender_name="my_username"))

        # But shouldn't do so if this is explicitly requested
        handler = EventHandler(
            Driver(),
            Settings(IGNORE_USERS=["ignore_me"]),
            plugins=PluginManager([]),
            ignore_own_messages=False,
        )
        assert not handler._should_ignore(create_message(sender_name="my_username"))

    @mock.patch("mmpy_bot.event_handler.EventHandler._handle_post")
    def test_handle_event(self, handle_post):
        handler = EventHandler(Driver(), Settings(), plugins=PluginManager([]))
        # This event should trigger _handle_post
        asyncio.run(handler._handle_event(json.dumps(create_message().body)))
        # This event should not
        asyncio.run(handler._handle_event(json.dumps({"event": "some_other_event"})))

        handle_post.assert_called_once_with(create_message().body)

    @mock.patch("mmpy_bot.driver.Driver.username", new="my_username")
    def test_handle_post(self):
        # Create an initialized plugin so its listeners are registered
        driver = Driver()
        plugin = ExamplePlugin().initialize(driver)
        # Construct a handler with it
        handler = EventHandler(driver, Settings(), plugins=PluginManager([plugin]))

        # Mock the call_function of the plugin so we can make some asserts
        async def mock_call_function(function, message, groups):
            # This is the regexp that we're trying to trigger
            assert function.matcher.pattern == "sleep ([0-9]+)"
            assert message.text == "sleep 5"  # username should be stripped off
            assert groups == ["5"]  # arguments should be matched and passed explicitly

        with mock.patch.object(
            plugin, "call_function", wraps=mock_call_function
        ) as mocked:
            # Transform the default message into a raw post event so we can pass it
            new_body = create_message(text="@my_username sleep 5").body.copy()
            new_body["data"]["post"] = json.dumps(new_body["data"]["post"])
            new_body["data"]["mentions"] = json.dumps(new_body["data"]["mentions"])
            asyncio.run(handler._handle_post(new_body))

            # Assert the function was called, so we know the asserts succeeded.
            mocked.assert_called_once()

    def test_handle_webhook(self):
        # Create an initialized plugin so its listeners are registered
        driver = Driver()
        plugin = WebHookExample().initialize(driver, Settings())
        # Construct a handler with it
        handler = EventHandler(driver, Settings(), plugins=PluginManager([plugin]))

        # Mock the call_function of the plugin so we can make some asserts
        async def mock_call_function(function, event, groups):
            # This is the regexp that we're trying to trigger
            assert function.matcher.pattern == "ping"
            assert event.text == "hello!"
            assert groups == []

        with mock.patch.object(
            plugin, "call_function", wraps=mock_call_function
        ) as mocked:
            asyncio.run(
                handler._handle_webhook(
                    WebHookEvent(
                        body={"text": "hello!"},
                        request_id="request_id",
                        webhook_id="ping",
                    ),
                )
            )
            # Assert the function was called, so we know the asserts succeeded.
            mocked.assert_called_once()
