import asyncio
import json
import logging
import queue
import re
from collections import defaultdict
from typing import Sequence

from mmpy_bot.driver import Driver
from mmpy_bot.plugins import PluginManager
from mmpy_bot.settings import Settings
from mmpy_bot.webhook_server import NoResponse
from mmpy_bot.wrappers import Message, WebHookEvent

log = logging.getLogger("mmpy.event_handler")


class EventHandler(object):
    def __init__(
        self,
        driver: Driver,
        settings: Settings,
        plugins: PluginManager,
        ignore_own_messages=True,
    ):
        """The EventHandler class takes care of the connection to mattermost and calling
        the appropriate response function to each event."""
        self.driver = driver
        self.settings = settings
        self.ignore_own_messages = ignore_own_messages
        self.plug_manager = plugins

        self._name_matcher = re.compile(rf"^@?{self.driver.username}\:?\s?")

        # Collect the listeners from all plugins
        self.message_listeners = defaultdict(list)
        self.webhook_listeners = defaultdict(list)

        for plugin in self.plug_manager:
            for matcher, functions in plugin.message_listeners.items():
                self.message_listeners[matcher].extend(functions)
            for matcher, functions in plugin.webhook_listeners.items():
                self.webhook_listeners[matcher].extend(functions)

        # PluginManager also has listeners for "help"
        for matcher, functions in self.plug_manager.message_listeners.items():
            self.message_listeners[matcher].extend(functions)

    def start(self):
        # This is blocking, will loop forever
        self.driver.init_websocket(self._handle_event)

    def _should_ignore(self, message: Message):
        # Ignore message from senders specified in settings, and maybe from ourself
        return (
            True
            if message.sender_name.lower()
            in (name.lower() for name in self.settings.IGNORE_USERS)
            else False
        ) or (self.ignore_own_messages and message.sender_name == self.driver.username)

    async def _check_queue_loop(self, webhook_queue: queue.Queue):
        log.info("EventHandlerWebHook queue listener started.")
        while True:
            try:
                event = webhook_queue.get_nowait()
                await self._handle_webhook(event)
            except queue.Empty:
                pass
            await asyncio.sleep(0.0001)

    async def _handle_event(self, data):
        post = json.loads(data)
        event_action = post.get("event")
        if event_action == "posted":
            await self._handle_post(post)

    async def _handle_post(self, post):
        # For some reason these are JSON strings, so need to parse them first
        for item in ["post", "mentions"]:
            if post.get("data", {}).get(item):
                post["data"][item] = json.loads(post["data"][item])

        # If the post starts with a mention of this bot, strip off that part.
        post["data"]["post"]["message"] = self._name_matcher.sub(
            "", post["data"]["post"]["message"]
        )
        message = Message(post)
        if self._should_ignore(message):
            return

        # Find all the listeners that match this message, and have their plugins handle
        # the rest.
        tasks = []
        for matcher, functions in self.message_listeners.items():
            match = matcher.match(message.text)
            if match:
                groups = list([group for group in match.groups() if group != ""])
                for function in functions:
                    # Create an asyncio task to handle this callback
                    tasks.append(
                        asyncio.create_task(
                            function.plugin.call_function(
                                function, message, groups=groups
                            )
                        )
                    )
        # Execute the callbacks in parallel
        asyncio.gather(*tasks)

    async def _handle_webhook(self, event: WebHookEvent):
        # Find all the listeners that match this webhook id, and have their plugins
        # handle the rest.
        tasks = []
        for matcher, functions in self.webhook_listeners.items():
            match = matcher.match(event.webhook_id)
            if match:
                for function in functions:
                    # Create an asyncio task to handle this callback
                    tasks.append(
                        asyncio.create_task(
                            function.plugin.call_function(function, event)
                        )
                    )
        # If this webhook doesn't correspond to any listeners, signal the WebHookServer
        # to not wait for any response
        if len(tasks) == 0:
            self.driver.respond_to_web(event, NoResponse)
        # If it does, execute the callbacks in parallel
        else:
            asyncio.gather(*tasks)
