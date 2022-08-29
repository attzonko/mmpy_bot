from __future__ import annotations

import asyncio
import inspect
import logging
import re
import shlex
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Union

import click

from mmpy_bot.utils import completed_future
from mmpy_bot.webhook_server import NoResponse
from mmpy_bot.wrappers import Message, WebHookEvent

if TYPE_CHECKING:
    from mmpy_bot.plugins import Plugin


log = logging.getLogger("mmpy.function")


class Function(ABC):
    def __init__(
        self,
        function: Union[Function, click.Command],
        matcher: re.Pattern,
        **metadata,
    ):
        # If another Function was passed, keep track of all these siblings.
        # We later use them to register not only the outermost Function, but also any
        # stacked ones.
        self.siblings = []

        while isinstance(function, Function):
            self.siblings.append(function)
            function = function.function

        if function is None:
            raise ValueError(
                "ERROR: Possible bug, inside the Function class function should not end up being None"
            )

        self.function = function
        self.is_coroutine = asyncio.iscoroutinefunction(function)
        self.is_click_function: bool = False
        self.matcher = matcher
        self.metadata = metadata

        if not isinstance(function, click.Command):
            self.function.callback = None
            self.function.get_help = None
            self.function.make_context = None
            self.function.invoke = None

        # To be set in the child class or from the parent plugin
        self.plugin: Optional[Plugin] = None
        self.name: Optional[str] = None
        self.docstring = self.function.__doc__ or ""

        @abstractmethod
        def __call__(self, *args):
            pass


class MessageFunction(Function):
    """Wrapper around a Plugin class method that should respond to certain Mattermost
    messages."""

    def __init__(
        self,
        *args,
        direct_only: bool = False,
        needs_mention: bool = False,
        silence_fail_msg: bool = False,
        allowed_users: Optional[Sequence[str]] = None,
        allowed_channels: Optional[Sequence[str]] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.is_click_function = isinstance(self.function, click.Command)
        self.direct_only = direct_only
        self.needs_mention = needs_mention
        self.silence_fail_msg = silence_fail_msg

        if allowed_users is None:
            self.allowed_users = []
        else:
            self.allowed_users = [user.lower() for user in allowed_users]

        if allowed_channels is None:
            self.allowed_channels = []
        else:
            self.allowed_channels = [channel.lower() for channel in allowed_channels]

        # Default for non-click functions
        _function: Union[Callable, click.Command] = self.function

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
                self.docstring += f"\n\n{self.function.get_help(ctx)}"

        if _function is not None:
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
            if self.silence_fail_msg is False:
                self.plugin.driver.reply_to(
                    message, "You do not have permission to perform this action!"
                )
            return return_value

        if self.allowed_channels and message.channel_name not in self.allowed_channels:
            if self.silence_fail_msg is False:
                self.plugin.driver.reply_to(
                    message, "You do not have permission to perform this action!"
                )
            return return_value

        if self.is_click_function:
            assert len(args) <= 1  # There is only one group, (.*)?
            if len(args) == 1:
                # Turn space-separated string into list
                args = tuple(shlex.split(args[0]))
            try:
                ctx = self.function.make_context(
                    info_name=self.plugin.__class__.__name__, args=list(args)
                )
                ctx.params.update({"self": self.plugin, "message": message})
                return self.function.invoke(ctx)
            # If there are any missing arguments or the function is otherwise called
            # incorrectly, send the click message back to the user and print help string.
            except (click.exceptions.ClickException, click.exceptions.Exit) as e:
                if isinstance(e, click.exceptions.Exit):
                    e = "Requested `--help`:"

                return self.plugin.driver.reply_to(message, f"{e}\n{self.docstring}")

        return self.function(self.plugin, message, *args)


def listen_to(
    regexp: str,
    regexp_flag: int = 0,
    *,
    direct_only=False,
    needs_mention=False,
    allowed_users=None,
    allowed_channels=None,
    silence_fail_msg=False,
    **metadata,
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
        new_func = MessageFunction(
            func,
            matcher=pattern,
            direct_only=direct_only,
            needs_mention=needs_mention,
            allowed_users=allowed_users,
            allowed_channels=allowed_channels,
            silence_fail_msg=silence_fail_msg,
            **metadata,
        )

        # Preserve docstring
        new_func.__doc__ = func.__doc__
        return new_func

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
    **metadata,
):
    """Wrap the given function in a WebHookFunction class with the specified regexp."""

    def wrapped_func(func):
        pattern = re.compile(regexp)
        new_func = WebHookFunction(
            func,
            matcher=pattern,
            **metadata,
        )

        # Preserve docstring
        new_func.__doc__ = func.__doc__
        return new_func

    return wrapped_func
