#!/usr/bin/env python
import sys
import logging
import logging.config

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
    '''
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)
    '''
    bot = LocalBot()
    bot.run()

if __name__ == '__main__':
    main()
