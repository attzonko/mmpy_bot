import asyncio
import logging
import sys
from typing import List, Optional, Union

from mmpy_bot.driver import Driver
from mmpy_bot.event_handler import EventHandler
from mmpy_bot.plugins import (
    ExamplePlugin,
    HelpPlugin,
    Plugin,
    PluginManager,
    WebHookExample,
)
from mmpy_bot.settings import Settings
from mmpy_bot.webhook_server import WebHookServer

log = logging.getLogger("mmpy.bot")


class Bot:
    """Base chatbot class.

    Can be either subclassed for custom functionality, or used as-is with custom plugins
    and settings. To start the bot, simply call bot.run().
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        plugins: Optional[Union[List[Plugin], PluginManager]] = None,
        enable_logging: bool = True,
    ):
        self._setup_plugin_manager(plugins)

        # Use default settings if none were specified.
        self.settings = settings or Settings()

        self.console = None

        if enable_logging:
            self._register_logger()

        self.driver = Driver(
            {
                "url": self.settings.MATTERMOST_URL,
                "port": self.settings.MATTERMOST_PORT,
                "token": self.settings.BOT_TOKEN,
                "scheme": self.settings.SCHEME,
                "verify": self.settings.SSL_VERIFY,
                "basepath": self.settings.MATTERMOST_API_PATH,
                "keepalive": True,
                "connect_kw_args": {"ping_interval": None},
            }
        )
        self.driver.login()
        self.plugin_manager.initialize(self.driver, self.settings)
        self.event_handler = EventHandler(
            self.driver, settings=self.settings, plugin_manager=self.plugin_manager
        )
        self.webhook_server = None

        if self.settings.WEBHOOK_HOST_ENABLED:
            self._initialize_webhook_server()

        self.running = False

    def _setup_plugin_manager(self, plugins):
        if plugins is None:
            self.plugin_manager = PluginManager(
                [HelpPlugin(), ExamplePlugin(), WebHookExample()]
            )
        elif isinstance(plugins, PluginManager):
            self.plugin_manager = plugins
        else:
            self.plugin_manager = PluginManager(plugins)

    def _register_logger(self):
        logging.basicConfig(
            **{
                "format": self.settings.LOG_FORMAT,
                "datefmt": self.settings.LOG_DATE_FORMAT,
                "level": logging.DEBUG if self.settings.DEBUG else logging.INFO,
                "filename": self.settings.LOG_FILE,
                "filemode": "w",
            }
        )
        # define and add a Handler which writes log messages to the sys.stdout
        # avoid double logging if no log file is specified
        if self.settings.LOG_FILE is not None:
            self.console = logging.StreamHandler(stream=sys.stdout)
            self.console.setFormatter(
                logging.Formatter(
                    self.settings.LOG_FORMAT, self.settings.LOG_DATE_FORMAT
                )
            )
            logging.getLogger("").addHandler(self.console)

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
        log.info(f"Starting bot {self.__class__.__name__}.")
        try:
            self.running = True

            self.driver.threadpool.start()
            # Start a thread to run potential scheduled jobs
            self.driver.threadpool.start_scheduler_thread(
                self.settings.SCHEDULER_PERIOD
            )
            # Start the webhook server on a separate thread if necessary
            if self.settings.WEBHOOK_HOST_ENABLED:
                self.driver.threadpool.start_webhook_server_thread(self.webhook_server)

            # Trigger "start" methods on every plugin
            self.plugin_manager.start()

            # Start listening for events
            self.event_handler.start()

        except KeyboardInterrupt as e:
            raise e

        finally:
            # When either the event handler finishes (if we asked it to stop) or we
            # receive a KeyboardInterrupt, shut down the bot.
            self.stop()

    def stop(self):
        if not self.running:
            return

        log.info("Stopping bot.")

        # Shutdown the running plugins
        self.plugin_manager.stop()

        # Stop the threadpool
        self.driver.threadpool.stop()
        self.running = False
