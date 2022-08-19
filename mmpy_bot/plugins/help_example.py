from __future__ import annotations

from mmpy_bot.driver import Driver
from mmpy_bot.function import listen_to
from mmpy_bot.plugins.base import Plugin, PluginManager
from mmpy_bot.settings import Settings
from mmpy_bot.wrappers import Message


def _custom_help_sort(rec):
    return (
        rec.metadata.get("category", ""),  # No categories first
        rec.help_type,
        rec.pattern.lstrip("^[(-"),
    )


def _prepare_function_help_message(h, string):
    cmd = h.metadata.get("human_description", h.pattern)
    direct = "`(*)`" if h.direct else ""
    mention = "`(+)`" if h.mention else ""

    if h.help_type == "webhook":
        string += f"- `{cmd}` {direct} {mention} - (webhook) {h.docheader}\n"
    else:
        if not h.docheader:
            string += f"- `{cmd}` {direct} {mention}\n"
        else:
            string += f"- `{cmd}` {direct} {mention} - {h.docheader}\n"

    return string


class HelpPlugin(Plugin):
    """Provide a `help` command that lists functions provided by all plugins.

    With a few plugins enabled the help text can become quite verbose. For this reason,
    this plugin defaults to sending a private/direct message with the information.

    If you wish to disable this behavior pass `direct_help=False` and the help text will
    be displayed in the channel where it is requested.
    """

    def __init__(
        self,
        direct_help: bool = True,
    ):
        super().__init__()
        self.direct_help: bool = direct_help

    def initialize(
        self,
        driver: Driver,
        plugin_manager: PluginManager,
        settings: Settings,
    ):
        super().initialize(driver, plugin_manager, settings)

        if self.settings.RESPOND_CHANNEL_HELP:
            self.help = listen_to("^!help$")(self.help)

    def get_help_string(self, message: Message) -> str:
        """Renders help information (FunctionInfo objects) into a markdown string.

        Help information is presented in a condensed format, grouped into categories
        """

        help_function_info = sorted(self.get_help(message), key=_custom_help_sort)

        string = "### The following functions have been registered:\n\n"
        string += "###### `(*)` require the use of `@botname`, "
        string += "`(+)` can only be used in direct message\n"
        old_category = None

        for h in help_function_info:
            # If categories are defined, group functions accordingly
            category = h.metadata.get("category")
            if category != old_category:
                old_category = category
                category = "uncategorized" if category is None else category
                string += f"Category `{category}`:\n"

            string = _prepare_function_help_message(h, string)

        return string

    def get_help(self, message: Message):
        """Obtain Help info from PluginManager.

        Override this method if you need to customize which listeners will be included
        in the help.
        """
        return self.plugin_manager.get_help()

    @listen_to("^help$", needs_mention=True)
    async def help(self, message: Message):
        """Shows this help information."""
        self.driver.reply_to(
            message, self.get_help_string(message), direct=self.direct_help
        )
