import asyncio
import logging
import sys
from typing import Optional, Sequence

from mmpy_bot.driver import Driver
from mmpy_bot.event_handler import EventHandler
from mmpy_bot.plugins import ExamplePlugin, Plugin, WebHookExample
from mmpy_bot.settings import Settings
from mmpy_bot.webhook_server import WebHookServer


class Bot:
    """Base chatbot class.

    Can be either subclassed for custom functionality, or used as-is with custom plugins
    and settings. To start the bot, simply call bot.run().
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        plugins: Optional[Sequence[Plugin]] = None,
    ):
        if plugins is None:
            plugins = [ExamplePlugin(), WebHookExample()]
        # Use default settings if none were specified.
        self.settings = settings or Settings()
        logging.basicConfig(
            **{
                "format": "[%(asctime)s] %(message)s",
                "datefmt": "%m/%d/%Y %H:%M:%S",
                "level": logging.DEBUG if self.settings.DEBUG else logging.INFO,
                "stream": sys.stdout,
            }
        )
        self.driver = Driver(
            {
                "url": self.settings.MATTERMOST_URL,
                "port": self.settings.MATTERMOST_PORT,
                "token": self.settings.BOT_TOKEN,
                "scheme": self.settings.SCHEME,
                "verify": self.settings.SSL_VERIFY,
            }
        )
        self.driver.login()
        self.plugins = self._initialize_plugins(plugins)
        self.event_handler = EventHandler(
            self.driver, settings=self.settings, plugins=self.plugins
        )
        self.webhook_server = None

        if self.settings.WEBHOOK_HOST_ENABLED:
            self._initialize_webhook_server()

    def _initialize_plugins(self, plugins: Sequence[Plugin]):
        for plugin in plugins:
            plugin.initialize(self.driver, self.settings)
        return plugins

    def _initialize_webhook_server(self):
        self.webhook_server = WebHookServer(
            url=self.settings.WEBHOOK_HOST_URL, port=self.settings.WEBHOOK_HOST_PORT
        )
        self.driver.register_webhook_server(self.webhook_server)
        # Schedule the queue loop to the current event loop so that it starts together
        # with self.init_websocket.
        asyncio.get_event_loop().create_task(
            self.event_handler._check_queue_loop(self.webhook_server.event_queue)
        )

    def run(self):
        logging.info(f"Starting bot {self.__class__.__name__}.")
        try:
            self.driver.threadpool.start()
            # Start a thread to run potential scheduled jobs
            self.driver.threadpool.start_scheduler_thread(
                self.settings.SCHEDULER_PERIOD
            )
            # Start the webhook server on a separate thread if necessary
            if self.settings.WEBHOOK_HOST_ENABLED:
                self.driver.threadpool.start_webhook_server_thread(self.webhook_server)

            for plugin in self.plugins:
                plugin.on_start()

            # Start listening for events
            self.event_handler.start()

        except KeyboardInterrupt as e:
            self.stop()
            raise e

    def stop(self):
        logging.info("Stopping bot.")
        # Shutdown the running plugins
        for plugin in self.plugins:
            plugin.on_stop()
        # Stop the threadpool
        self.driver.threadpool.stop()
