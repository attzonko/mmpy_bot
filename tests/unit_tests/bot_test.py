import logging
from unittest import mock

import pytest

from mmpy_bot import Bot, ExamplePlugin, Settings
from mmpy_bot.plugins import PluginManager

from ..integration_tests.utils import TestPlugin


@pytest.fixture(scope="function")
def bot():
    # Patch login to avoid sending requests to the internet
    with mock.patch("mmpy_bot.driver.Driver.login") as login:
        bot = Bot(plugins=[ExamplePlugin()], settings=Settings(LOG_LEVEL=logging.DEBUG))
        login.assert_called_once()
        yield bot
        bot.stop()  # if the bot was started, stop it


class TestBot:
    @mock.patch("mmpy_bot.driver.Driver.login")
    def test_init(self, login):
        # Create some plugins and mock their initialize method so we can check calls
        plugins = [ExamplePlugin(), TestPlugin()]
        for plugin in plugins:
            plugin.initialize = mock.MagicMock()

        settings = Settings(MATTERMOST_URL="test_url.org", BOT_TOKEN="random_token")
        # Create a bot and verify that it gets initialized correctly
        bot = Bot(
            settings=settings,
            plugins=plugins,
        )
        assert bot.driver.options["url"] == "test_url.org"
        assert bot.driver.options["token"] == "random_token"
        assert isinstance(bot.plugin_manager, PluginManager)
        assert bot.plugin_manager.plugins == plugins
        login.assert_called_once()

        # Verify that all of the passed plugins were initialized
        for plugin in plugins:
            plugin.initialize.assert_called_once_with(
                bot.driver, bot.plugin_manager, settings
            )

    @mock.patch.multiple("mmpy_bot.Plugin", on_start=mock.DEFAULT, on_stop=mock.DEFAULT)
    def test_run(self, bot, **mocks):
        with mock.patch.object(bot.driver, "init_websocket") as init_websocket:
            bot.run()
            init_websocket.assert_called_once()

            for plugin in bot.plugin_manager.plugins:
                plugin.on_start.assert_called_once()

            bot.stop()

            for plugin in bot.plugin_manager.plugins:
                plugin.on_stop.assert_called_once()
