from __future__ import annotations

import logging
import re
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from mmpy_bot.driver import Driver
from mmpy_bot.function import Function, MessageFunction, WebHookFunction, listen_to
from mmpy_bot.settings import Settings
from mmpy_bot.wrappers import EventWrapper, Message

log = logging.getLogger("mmpy.plugin_base")


class Plugin(ABC):
    """A Plugin is a self-contained class that defines what functions should be executed
    given different inputs.

    It will be called by the EventHandler whenever one of its listeners is triggered,
    but execution of the corresponding function is handled by the plugin itself. This
    way, you can implement multithreading or multiprocessing as desired.
    """

    def __init__(
        self,
        help_trigger: bool = False,
        help_trigger_bang: bool = False,
        direct_help: bool = False,
    ):
        self.driver: Optional[Driver] = None
        self.message_listeners: Dict[
            re.Pattern, Sequence[MessageFunction]
        ] = defaultdict(list)
        self.webhook_listeners: Dict[
            re.Pattern, Sequence[WebHookFunction]
        ] = defaultdict(list)
        self.direct_help: bool = direct_help

        # We have to register the help function listeners at runtime to prevent the
        # Function object from being shared across different Plugins.
        # This code is a bit hairy because the function signature of an
        # instance is (message) not (self, message) causing failures later
        if help_trigger:
            self.help = listen_to("^help$", needs_mention=True)(Plugin.help)
        if help_trigger_bang:
            if not help_trigger:
                self.help = listen_to("^!help$")(Plugin.help)
            else:
                self.help = listen_to("^!help$")(self.help)

    def initialize(self, driver: Driver, settings: Optional[Settings] = None):
        self.driver = driver

        # Register listeners for any listener functions we might have
        for attribute in dir(self):
            attribute = getattr(self, attribute)
            if isinstance(attribute, Function):
                # Register this function and any potential siblings
                for function in [attribute] + attribute.siblings:
                    function.plugin = self
                    if isinstance(function, MessageFunction):
                        self.message_listeners[function.matcher].append(function)
                    elif isinstance(function, WebHookFunction):
                        self.webhook_listeners[function.matcher].append(function)
                    else:
                        raise TypeError(
                            f"{self.__class__.__name__} has a function of unsupported"
                            f" type {type(function)}."
                        )

        return self

    def on_start(self):
        """Will be called after initialization.

        Can be overridden on the subclass if desired.
        """
        log.debug(f"Plugin {self.__class__.__name__} started!")
        return self

    def on_stop(self):
        """Will be called when the bot is shut down manually.

        Can be overridden on the subclass if desired.
        """
        log.debug(f"Plugin {self.__class__.__name__} stopped!")
        return self

    def get_help_string(self):
        string = f"Plugin {self.__class__.__name__} has the following functions:\n"
        string += "----\n"
        for functions in self.message_listeners.values():
            for function in functions:
                string += f"- {function.get_help_string()}"
            string += "----\n"
        if len(self.webhook_listeners) > 0:
            string += "### Registered webhooks:\n"
            for functions in self.webhook_listeners.values():
                for function in functions:
                    string += f"- {function.get_help_string()}"

        return string

    async def call_function(
        self,
        function: Function,
        event: EventWrapper,
        groups: Optional[Sequence[str]] = [],
    ):
        if function.is_coroutine:
            await function(event, *groups)  # type:ignore
        else:
            # By default, we use the global threadpool of the driver, but we could use
            # a plugin-specific thread or process pool if we wanted.
            self.driver.threadpool.add_task(function, event, *groups)

    async def help(self, message: Message):
        """Prints the list of functions registered on every active plugin."""
        if self.direct_help:
            self.driver.reply_to(message, self.get_help_string(), direct=True)
        else:
            self.driver.reply_to(message, self.get_help_string())


@dataclass
class PluginHelp:
    help_type: str
    location: str
    function: str
    pattern: str
    doc_header: str
    doc_full: str
    annotations: Dict


class PluginManager:
    """PluginManager is responsible for initializing all plugins and display aggregated
    help from each of them.

    It is supposed to be transparent to EventHandler that interacts directly with each
    individual Plugin.
    """

    def __init__(
        self,
        plugins: Sequence[Plugin],
        help_trigger: bool = True,
        help_trigger_bang: bool = False,
        direct_help: bool = True,
    ):
        self.driver: Optional[Driver] = None
        self.plugins: Sequence[Plugin] = plugins
        self.direct_help: bool = direct_help

        self.message_listeners: Dict[
            re.Pattern, Sequence[MessageFunction]
        ] = defaultdict(list)

        # This code is a bit hairy because the function signature of an
        # instance is (message) not (self, message) causing failures later
        if help_trigger:
            self.help = listen_to("^help$", needs_mention=True)(PluginManager.help)
        if help_trigger_bang:
            if not help_trigger:
                self.help = listen_to("^!help$")(PluginManager.help)
            else:
                self.help = listen_to("^!help$")(self.help)

    def __iter__(self):
        return iter(self.plugins)

    def initialize(self, driver: Driver, settings: Optional[Settings] = None):
        self.driver = driver

        # Add Plugin manager help to message listeners
        self.help.plugin = self
        self.message_listeners[self.help.matcher].append(self.help)

        for plugin in self.plugins:
            plugin.initialize(self.driver, settings)

    def get_help(self):
        response: List[PluginHelp] = []

        for plugin in self.plugins:
            for matcher, functions in plugin.message_listeners.items():
                for function in functions:
                    response.append(
                        PluginHelp(
                            help_type="message",
                            location=self.__class__.__name__,
                            function=function,
                            pattern=matcher.pattern,
                            doc_header=function.function.__doc__.split("\n", 1)[0],
                            doc_full=function.function.__doc__,
                            annotations=function.annotations,
                        )
                    )

            if len(plugin.webhook_listeners) > 0:
                for matcher, functions in plugin.webhook_listeners.items():
                    for function in functions:
                        response.append(
                            PluginHelp(
                                help_type="webhook",
                                location=self.__class__.__name__,
                                function=function,
                                pattern=matcher.pattern,
                                doc_header=function.function.__doc__.split("\n", 1)[0],
                                doc_full=function.function.__doc__,
                                annotations=function.annotations,
                            )
                        )

        return response

    def get_help_string(self):
        def custom_sort(rec):
            return (rec.help_type, rec.pattern.lstrip("^[(-"))

        string = "## The following functions have been registered:\n\n"
        for h in sorted(self.get_help(), key=custom_sort):
            cmd = h.annotations.get("syntax", h.pattern)
            if h.help_type == "webhook":
                string += f"- `{cmd}` - (webhook) {h.doc_header}\n"
            else:
                string += f"- `{cmd}` - {h.doc_header}\n"

        return string

    async def help(self, message: Message):
        """Prints the help message in a channel or privately."""
        if self.direct_help:
            self.driver.reply_to(message, self.get_help_string(), direct=True)
        else:
            self.driver.reply_to(message, self.get_help_string())
