from __future__ import annotations

import logging
import re
from abc import ABC
from collections import defaultdict
from typing import Dict, Optional, Sequence

from mmpy_bot.driver import Driver
from mmpy_bot.function import Function, MessageFunction, WebHookFunction, listen_to
from mmpy_bot.settings import Settings
from mmpy_bot.wrappers import EventWrapper, Message

log = logging.getLogger("mmpy.plugin_base")


class PluginMixin:
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
        self.driver.reply_to(message, self.get_help_string())


class Plugin(ABC, PluginMixin):
    """A Plugin is a self-contained class that defines what functions should be executed
    given different inputs.

    It will be called by the EventHandler whenever one of its listeners is triggered,
    but execution of the corresponding function is handled by the plugin itself. This
    way, you can implement multithreading or multiprocessing as desired.
    """

    def __init__(self, help_trigger=False, help_trigger_nomention=False):
        self.driver: Optional[Driver] = None
        self.message_listeners: Dict[
            re.Pattern, Sequence[MessageFunction]
        ] = defaultdict(list)
        self.webhook_listeners: Dict[
            re.Pattern, Sequence[WebHookFunction]
        ] = defaultdict(list)

        # We have to register the help function listeners at runtime to prevent the
        # Function object from being shared across different Plugins.
        # This code is a bit hairy because the function signature of an
        # instance is (message) not (self, message) causing failures later
        if help_trigger:
            self.help = listen_to("^help$", needs_mention=True)(PluginMixin.help)
        if help_trigger_nomention:
            if not help_trigger:
                self.help = listen_to("^!help$")(PluginMixin.help)
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


class PluginManager(PluginMixin):
    def __init__(self, plugins: Sequence[Plugin], help_trigger=True):
        self.driver: Optional[Driver] = None
        self.plugins: Sequence[Plugin] = plugins

        self.message_listeners: Dict[
            re.Pattern, Sequence[MessageFunction]
        ] = defaultdict(list)

        # This code is a bit hairy because the function signature of an
        # instance is (message) not (self, message) causing failures later
        if help_trigger:
            self.help = listen_to("^help$", needs_mention=True)(PluginMixin.help)
        if help_trigger_nomention:
            if not help_trigger:
                self.help = listen_to("^!help$")(PluginMixin.help)
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
