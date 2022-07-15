import asyncio
from unittest import mock

from mmpy_bot import Plugin, Settings, listen_to
from mmpy_bot.driver import Driver
from mmpy_bot.plugins import PluginManager

from .event_handler_test import create_message


# Used in the plugin tests below
class FakePlugin(Plugin):
    @listen_to("pattern", needs_mention=True)
    def my_function(self, message, another_arg=True):
        """This is the docstring of my_function."""
        pass

    @listen_to("async_pattern")
    @listen_to("another_async_pattern", direct_only=True)
    async def my_async_function(self, message):
        """Async function docstring."""
        pass


class TestPlugin:
    @mock.patch("mmpy_bot.driver.ThreadPool.add_task")
    def test_call_function(self, add_task):
        p = FakePlugin()
        # Functions only listen for events when initialized via PluginManager
        PluginManager([p]).initialize(Driver(), Settings())

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
