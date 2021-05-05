import asyncio
import re
from unittest import mock

import click

from mmpy_bot import Plugin, listen_to, listen_webhook
from mmpy_bot.driver import Driver

from .event_handler_test import create_message


# Used in the plugin tests below
class FakePlugin(Plugin):
    @listen_to("pattern")
    def my_function(self, message, needs_mention=True):
        """This is the docstring of my_function."""
        pass

    @listen_to("direct_pattern", direct_only=True, allowed_users=["admin"])
    def direct_function(self, message):
        pass

    @listen_to("async_pattern")
    @listen_to("another_async_pattern", direct_only=True)
    async def my_async_function(self, message):
        """Async function docstring."""
        pass

    @listen_to("click_command")
    @click.command(help="Help string for the entire function.")
    @click.option(
        "--option", type=int, default=0, help="Help string for the optional argument."
    )
    def click_commmand(self, message, option):
        """Ignored docstring.

        Just for code readability.
        """
        pass

    @listen_webhook("webhook_id")
    def webhook_listener(self, event):
        """A webhook function."""
        pass


class TestPlugin:
    def test_initialize(self):
        p = FakePlugin().initialize(Driver())
        # Test whether the function was registered properly
        assert p.message_listeners[re.compile("pattern")] == [
            FakePlugin.my_function,
        ]

        # This function should be registered twice, once for each listener
        assert len(p.message_listeners[re.compile("async_pattern")]) == 1
        assert (
            p.message_listeners[re.compile("async_pattern")][0].function
            == FakePlugin.my_async_function.function
        )

        assert len(p.message_listeners[re.compile("another_async_pattern")]) == 1
        assert (
            p.message_listeners[re.compile("another_async_pattern")][0].function
            == FakePlugin.my_async_function.function
        )

        assert len(p.webhook_listeners) == 1
        assert p.webhook_listeners[re.compile("webhook_id")] == [
            FakePlugin.webhook_listener
        ]

    @mock.patch("mmpy_bot.driver.ThreadPool.add_task")
    def test_call_function(self, add_task):
        p = FakePlugin().initialize(Driver())

        # Since this is not an async function, a task should be added to the threadpool
        message = create_message(text="pattern")
        asyncio.run(
            p.call_function(FakePlugin.my_function, message, groups=["test", "another"])
        )
        add_task.assert_called_once_with(
            FakePlugin.my_function, message, "test", "another"
        )

        # Since this is an async function, it should be called directly through asyncio.
        message = create_message(text="async_pattern")
        with mock.patch.object(p.my_async_function, "function") as mock_function:
            asyncio.run(
                p.call_function(FakePlugin.my_async_function, message, groups=[])
            )
            mock_function.assert_called_once_with(p, message)

    def test_help_string(self, snapshot):
        p = FakePlugin(help_trigger=True, help_trigger_bang=True).initialize(Driver())
        # Compare the help string with the snapshotted version.
        snapshot.assert_match(p.get_help_string())

    def test_no_help_trigger(self, snapshot):
        p = FakePlugin().initialize(Driver())
        # Compare the help string with the snapshotted version.
        snapshot.assert_match(p.get_help_string())
