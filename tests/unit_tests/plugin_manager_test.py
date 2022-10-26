import re
from unittest import mock

import click

from mmpy_bot import Plugin, Settings, listen_to, listen_webhook
from mmpy_bot.driver import Driver
from mmpy_bot.plugins import PluginManager


# Used in the plugin tests below
class FakePlugin(Plugin):
    """Hello FakePlugin.

    This is a plugin level docstring
    """

    @listen_to("pattern", needs_mention=True)
    def my_function(self, message, another_arg=True):
        """This is the docstring of my_function."""
        pass

    @listen_to("direct_pattern", direct_only=True, allowed_users=["admin"])
    def direct_function(self, message):
        """Help direct function."""
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
        """Extended docstring.

        This docstring will have 'click --help' appended
        """
        pass

    @listen_to("hi_custom", custom="Custom attribute")
    def hi_custom(self, message):
        """A custom function."""
        pass

    @listen_webhook("webhook_id")
    def webhook_listener(self, event):
        """A webhook function."""
        pass


def expand_func_names(f):
    return [f] + f.siblings


msg_listeners = {
    re.compile("pattern"): expand_func_names(FakePlugin.my_function),
    re.compile("direct_pattern"): expand_func_names(FakePlugin.direct_function),
    re.compile("another_async_pattern"): expand_func_names(
        FakePlugin.my_async_function
    ),
    re.compile("async_pattern"): expand_func_names(FakePlugin.my_async_function),
    re.compile("hi_custom"): expand_func_names(FakePlugin.hi_custom),
    # Click commands construct a regex pattern from the listen_to pattern
    re.compile("^click_command(?: |$)(.*)?"): expand_func_names(
        FakePlugin.click_commmand
    ),
}

hook_listeners = {
    re.compile("webhook_id"): expand_func_names(FakePlugin.webhook_listener)
}


class TestPlugin:
    def test_init_plugin(self):
        p = FakePlugin()
        m = PluginManager([p])
        with mock.patch.object(p, "initialize") as mocked:
            m.initialize(Driver(), Settings())

            mocked.assert_called_once()

    def test_initialize(self):
        m = PluginManager([FakePlugin()])
        m.initialize(Driver(), Settings())

        # Test whether the function was registered properly
        assert m.message_listeners[re.compile("pattern")] == [
            FakePlugin.my_function,
        ]

        # This function should be registered twice, once for each listener
        assert len(m.message_listeners[re.compile("async_pattern")]) == 1
        assert (
            m.message_listeners[re.compile("async_pattern")][0].function
            == FakePlugin.my_async_function.function
        )

        assert len(m.message_listeners[re.compile("another_async_pattern")]) == 1
        assert (
            m.message_listeners[re.compile("another_async_pattern")][0].function
            == FakePlugin.my_async_function.function
        )

        assert len(m.webhook_listeners) == 1
        assert m.webhook_listeners[re.compile("webhook_id")] == [
            FakePlugin.webhook_listener
        ]


class TestPluginManager:
    def setup_method(self):
        self.p = FakePlugin()
        self.plugin_manager = PluginManager([self.p])

    def test_init(self):
        self.plugin_manager.initialize(Driver(), Settings())

        # Test that listeners of individual plugins are now registered on the plugin_manager
        assert len(msg_listeners) == len(self.plugin_manager.message_listeners)
        for pattern, listeners in self.plugin_manager.message_listeners.items():
            for listener in listeners:
                assert pattern in msg_listeners
                assert listener in msg_listeners[pattern]

        assert len(hook_listeners) == len(self.plugin_manager.webhook_listeners)
        for pattern, listeners in self.plugin_manager.webhook_listeners.items():
            for listener in listeners:
                assert pattern in hook_listeners
                assert listener in hook_listeners[pattern]

    def test_get_help(self):
        # Prior to initialization there is no help
        assert self.plugin_manager.get_help() == []

        self.plugin_manager.initialize(Driver(), Settings())

        assert len(self.plugin_manager.get_help()) != 0

        for hlp in self.plugin_manager.get_help():
            assert hlp.location == "FakePlugin"
            assert (
                hlp.function.plugin.__doc__
                == """Hello FakePlugin.

    This is a plugin level docstring
    """
            )
            assert hlp.is_click == hlp.function.is_click_function
            assert hlp.docfull.startswith(hlp.function.__doc__)

            if hlp.pattern in ["direct_pattern", "another_async_pattern"]:
                assert hlp.direct
            else:
                assert not hlp.direct

            if hlp.pattern in ["pattern"]:
                assert hlp.mention
            else:
                assert not hlp.mention

            if hlp.help_type == "message":
                assert hlp.pattern in map(lambda x: x.pattern, msg_listeners)
            elif hlp.help_type == "webhook":
                assert hlp.pattern in map(lambda x: x.pattern, hook_listeners)
