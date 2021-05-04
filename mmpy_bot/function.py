from __future__ import annotations

import asyncio
import inspect
import logging
import re
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Sequence

import click

from mmpy_bot.utils import completed_future, spaces
from mmpy_bot.webhook_server import NoResponse
from mmpy_bot.wrappers import Message, WebHookEvent

log = logging.getLogger("mmpy.function")


class Function(ABC):
    def __init__(
        self,
        function: Callable,
        matcher: re.Pattern,
        annotations: Optional[Dict] = None,
    ):
        # If another Function was passed, keep track of all these siblings.
        # We later use them to register not only the outermost Function, but also any
        # stacked ones.
        self.siblings = []
        while isinstance(function, Function):
            self.siblings.append(function)
            function = function.function

        self.function = function
        self.is_coroutine = asyncio.iscoroutinefunction(function)
        self.matcher = matcher
        self.annotations = annotations if annotations is not None else {}

        # To be set in the child class or from the parent plugin
        self.plugin = None
        self.name: Optional[str] = None
        self.docstring: Optional[str] = None

        @abstractmethod
        def __call__(self, *args):
            pass

    def get_help_string(self):
        string = f"`{self.matcher.pattern}`:\n"
        # Add a docstring
        doc = self.docstring or "No description provided."
        string += f"{spaces(8)}{doc}\n"
        return string


class MessageFunction(Function):
    """Wrapper around a Plugin class method that should respond to certain Mattermost
    messages."""

    def __init__(
        self,
        *args,
        direct_only: bool = False,
        needs_mention: bool = False,
        allowed_users: Optional[Sequence[str]] = None,
        allowed_channels: Optional[Sequence[str]] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.is_click_function = isinstance(self.function, click.Command)
        self.direct_only = direct_only
        self.needs_mention = needs_mention

        if allowed_users is None:
            self.allowed_users = []
        else:
            self.allowed_users = [user.lower() for user in allowed_users]

        if allowed_channels is None:
            self.allowed_channels = []
        else:
            self.allowed_channels = [channel.lower() for channel in allowed_channels]

        if self.is_click_function:
            _function = self.function.callback
            if asyncio.iscoroutinefunction(_function):
                raise ValueError(
                    "Combining click functions and coroutines is currently not supported!"
                    " Consider using a regular function, which will be threaded by default."
                )
            with click.Context(
                self.function,
                info_name=self.matcher.pattern.strip("^").split(" (.*)?")[0],
            ) as ctx:
                # Get click help string and do some extra formatting
                self.docstring = self.function.get_help(ctx).replace(
                    "\n", f"\n{spaces(8)}"
                )
        else:
            _function = self.function
            self.docstring = self.function.__doc__

        self.name = _function.__qualname__

        argspec = list(inspect.signature(_function).parameters.keys())
        if not argspec[:2] == ["self", "message"]:
            raise TypeError(
                "Any message listener function should at least have the positional"
                f" arguments `self` and `message`, but function {self.name} has"
                f" arguments {argspec}."
            )

    def __call__(self, message: Message, *args):
        # We need to return this so that if this MessageFunction was called with `await`,
        # asyncio doesn't crash.
        return_value = None if not self.is_coroutine else completed_future()

        # Check if this message meets our requirements
        if self.direct_only and not message.is_direct_message:
            return return_value

        if self.needs_mention and not (
            message.is_direct_message or self.plugin.driver.user_id in message.mentions
        ):
            return return_value

        if self.allowed_users and message.sender_name not in self.allowed_users:
            self.plugin.driver.reply_to(
                message, "You do not have permission to perform this action!"
            )
            return return_value

        if self.allowed_channels and message.channel_name not in self.allowed_channels:
            self.plugin.driver.reply_to(
                message, "You do not have permission to perform this action!"
            )
            return return_value

        if self.is_click_function:
            assert len(args) <= 1  # There is only one group, (.*)?
            if len(args) == 1:
                # Turn space-separated string into list
                args = args[0].strip(" ").split(" ")
            try:
                ctx = self.function.make_context(
                    info_name=self.plugin.__class__.__name__, args=list(args)
                )
                ctx.params.update({"self": self.plugin, "message": message})
                return self.function.invoke(ctx)
            # If there are any missing arguments or the function is otherwise called
            # incorrectly, send the click message back to the user and print help string.
            except click.exceptions.ClickException as e:
                return self.plugin.driver.reply_to(message, f"{e}\n{self.docstring}")

        return self.function(self.plugin, message, *args)

    def get_help_string(self):
        string = super().get_help_string()
        if any(
            [
                self.needs_mention,
                self.direct_only,
                self.allowed_users,
                self.allowed_channels,
            ]
        ):
            # Print some information describing the usage settings.
            string += f"{spaces(4)}Additional information:\n"
            if self.needs_mention:
                string += (
                    f"{spaces(4)}- Needs to either mention @{self.plugin.driver.username}"
                    " or be a direct message.\n"
                )
            if self.direct_only:
                string += f"{spaces(4)}- Needs to be a direct message.\n"

            if self.allowed_users:
                string += f"{spaces(4)}- Restricted to certain users.\n"

            if self.allowed_channels:
                string += f"{spaces(4)}- Restricted to certain channels.\n"

        return string


def listen_to(
    regexp: str,
    regexp_flag: int = 0,
    *,
    direct_only=False,
    needs_mention=False,
    allowed_users=None,
    allowed_channels=None,
    annotations=None,
):
    """Wrap the given function in a MessageFunction class so we can register some
    properties."""

    if allowed_users is None:
        allowed_users = []

    if allowed_channels is None:
        allowed_channels = []

    def wrapped_func(func):
        reg = regexp
        if isinstance(func, click.Command):
            if "$" in regexp:
                raise ValueError(
                    f"Regexp of function {func.callback} contains a $, which is not"
                    " supported! The regexp should simply reflect the argument name, and"
                    " click will take care of the rest."
                )

            # Modify the regexp so that it won't try to match the individual arguments.
            # Click will take care of those. We also manually add the ^ if necessary,
            # so that the commands can't be inserted in the middle of a sentence.
            reg = f"^{reg.strip('^')} (.*)?"  # noqa

        pattern = re.compile(reg, regexp_flag)
        return MessageFunction(
            func,
            matcher=pattern,
            direct_only=direct_only,
            needs_mention=needs_mention,
            allowed_users=allowed_users,
            allowed_channels=allowed_channels,
            annotations=annotations,
        )

    return wrapped_func


class WebHookFunction(Function):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if isinstance(self.function, click.Command):
            raise TypeError(
                "Webhook functions can't be click commands, since they don't take any"
                " additional arguments!"
            )

        self.name = self.function.__qualname__
        self.docstring = self.function.__doc__

        argspec = list(inspect.signature(self.function).parameters.keys())
        if not argspec == ["self", "event"]:
            raise TypeError(
                "A webhook listener function should have exactly two arguments:"
                f" `self` and `event`, but function {self.name} has arguments {argspec}."
            )

    def __call__(self, event: WebHookEvent):
        # Signal the WebHookServer that we won't be sending a response.
        def ensure_response(*args):
            if not event.responded:
                self.plugin.driver.respond_to_web(event, NoResponse)

        # If this is a coroutine, wrap it in a task with ensure_response as callback
        if self.is_coroutine:
            task = asyncio.create_task(self.function(self.plugin, event))
            task.add_done_callback(ensure_response)
            return task

        # If not, simply call both of these functions
        try:
            self.function(self.plugin, event)
        except Exception:
            log.exception("Exception occurred: ")
        finally:
            return ensure_response()


def listen_webhook(
    regexp: str,
):
    """Wrap the given function in a WebHookFunction class with the specified regexp."""

    def wrapped_func(func):
        pattern = re.compile(regexp)
        return WebHookFunction(
            func,
            matcher=pattern,
        )

    return wrapped_func
