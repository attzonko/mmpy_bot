from __future__ import annotations

import logging
import re
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from mmpy_bot.driver import Driver
from mmpy_bot.function import Function, MessageFunction, WebHookFunction
from mmpy_bot.settings import Settings
from mmpy_bot.utils import split_docstring
from mmpy_bot.wrappers import EventWrapper

log = logging.getLogger("mmpy.plugin_base")


class Plugin(ABC):
    """A Plugin is a self-contained class that defines what functions should be executed
    given different inputs.

    It will be called by the EventHandler whenever one of its listeners is triggered,
    but execution of the corresponding function is handled by the plugin itself. This
    way, you can implement multithreading or multiprocessing as desired.
    """

    def __init__(self):
        self.driver: Optional[Driver] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.settings: Optional[Settings] = None
        self.docstring = self.__doc__ if self.__doc__ != Plugin.__doc__ else None

    def initialize(
        self,
        driver: Driver,
        plugin_manager: PluginManager,
        settings: Settings,
    ):
        self.driver = driver
        self.plugin_manager = plugin_manager
        self.settings = settings

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


@dataclass
class FunctionInfo:
    help_type: str
    location: str
    function: Function
    pattern: str
    docheader: str
    docfull: str
    direct: bool
    mention: bool
    is_click: bool
    metadata: Dict


def get_function_characteristics(function):
    """Returns a tuple describing the function user interface.

    Returns (direct_only, needs_mention, help_type)
    """
    if isinstance(function, MessageFunction):
        return (function.direct_only, function.needs_mention, "message")
    elif isinstance(function, WebHookFunction):
        return (False, False, "webhook")
    else:
        raise NotImplementedError(
            f"Unknown/Unsupported listener type: '{type(function)}'"
        )


def generate_plugin_help(
    listeners: Dict[re.Pattern[Any], List[Union[MessageFunction, WebHookFunction]]],
):
    """Build FunctionInfo objects from plugin and function information.

    Returns one FunctionInfo instance for every listener (message or webhook)
    """

    plug_help: List[FunctionInfo] = []

    for matcher, functions in listeners.items():
        for function in functions:
            plug_head, plug_full = split_docstring(function.plugin.__doc__)
            func_head, func_full = split_docstring(function.docstring)
            direct, mention, help_type = get_function_characteristics(function)

            plug_help.append(
                FunctionInfo(
                    help_type=help_type,
                    location=function.plugin.__class__.__name__,
                    function=function,
                    pattern=matcher.pattern,
                    docheader=func_head,
                    docfull=func_full,
                    direct=direct,
                    mention=mention,
                    is_click=function.is_click_function,
                    metadata=function.metadata,
                )
            )

    return plug_help


class PluginManager:
    """PluginManager is responsible for initializing all plugins and display aggregated
    help from each of them.

    It is supposed to be transparent to EventHandler that interacts directly with each
    individual Plugin.
    """

    def __init__(
        self,
        plugins: Sequence[Plugin],
    ):
        self.settings: Optional[Settings] = None
        self.plugins = plugins

        self.message_listeners: Dict[re.Pattern, List[MessageFunction]] = defaultdict(
            list
        )
        self.webhook_listeners: Dict[re.Pattern, List[WebHookFunction]] = defaultdict(
            list
        )

    def initialize(self, driver: Driver, settings: Settings):
        for plugin in self.plugins:
            plugin.initialize(driver, self, settings)

            # Register listeners for any listener functions in the plugin
            for attribute in dir(plugin):
                attribute = getattr(plugin, attribute)
                if not isinstance(attribute, Function):
                    continue

                # Register this function and any potential siblings
                for function in [attribute] + attribute.siblings:
                    # Plugin message/webhook handlers can be decorated multiple times
                    # resulting in multiple siblings that do not have .plugin defined
                    # or where the relationship with the parent plugin is incorrect
                    function.plugin = plugin
                    if isinstance(function, MessageFunction):
                        self.message_listeners[function.matcher].append(function)
                    elif isinstance(function, WebHookFunction):
                        self.webhook_listeners[function.matcher].append(function)
                    else:
                        raise TypeError(
                            f"{plugin.__class__.__name__} has a function of unsupported"
                            f" type {type(function)}."
                        )

    def start(self):
        """Trigger on_start() on every registered plugin."""
        for plugin in self.plugins:
            plugin.on_start()

    def stop(self):
        """Trigger on_stop() on every registered plugin."""
        for plugin in self.plugins:
            plugin.on_stop()

    def get_help(self) -> List[FunctionInfo]:
        """Returns a list of FunctionInfo items for every registered message and webhook
        listener."""
        plug_help = generate_plugin_help(self.message_listeners)
        plug_help += generate_plugin_help(self.webhook_listeners)

        return plug_help
