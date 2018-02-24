#!/usr/bin/env python
from mattermost_bot.bot import Bot, PluginsManager
from mattermost_bot.mattermost_v4 import MattermostClientv4
from mattermost_bot.dispatcher import MessageDispatcher
import bot_settings

class LocalBot(Bot):

    def __init__(self):
        self._client = MattermostClientv4(
            bot_settings.BOT_URL, bot_settings.BOT_TEAM,
            bot_settings.BOT_LOGIN, bot_settings.BOT_PASSWORD,
            bot_settings.SSL_VERIFY
            )
        self._plugins = PluginsManager()
        self._plugins.init_plugins()
        self._dispatcher = MessageDispatcher(self._client, self._plugins)

def main():
    bot = LocalBot()
    bot.run()

if __name__ == '__main__':
    main()
