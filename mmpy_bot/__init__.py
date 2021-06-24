from pathlib import Path

from mmpy_bot.bot import Bot
from mmpy_bot.function import (
    MessageFunction,
    WebHookFunction,
    listen_to,
    listen_webhook,
)
from mmpy_bot.plugins import ExamplePlugin, Plugin, WebHookExample
from mmpy_bot.scheduler import schedule
from mmpy_bot.settings import Settings
from mmpy_bot.wrappers import ActionEvent, Message, WebHookEvent

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().rstrip()

__all__ = [
    "__version__",
    "Bot",
    "MessageFunction",
    "WebHookFunction",
    "listen_to",
    "listen_webhook",
    "ExamplePlugin",
    "Plugin",
    "WebHookExample",
    "schedule",
    "Settings",
    "ActionEvent",
    "Message",
    "WebHookEvent",
]
