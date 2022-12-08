#!/usr/bin/env python
import os
from dotenv import load_dotenv
from mmpy_bot import Bot, Settings
from rebecca_plugin.rebecca import MyPlugin  # <== Example of importing your own plugin, don't forget to add it to the plugins list.

load_dotenv()

MATTERMOST_URL = os.getenv("MATTERMOST_URL")
MATTERMOST_PORT = os.getenv("MATTERMOST_PORT")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_TEAM = os.getenv("BOT_TEAM")

bot = Bot(
    settings=Settings(
        MATTERMOST_URL = MATTERMOST_URL,
        MATTERMOST_PORT = MATTERMOST_PORT,
        BOT_TOKEN = BOT_TOKEN,
        BOT_TEAM = BOT_TEAM,
        SSL_VERIFY = True,
    ),
    plugins=[MyPlugin()],
)
print(os.getenv("TEST"))
bot.run()
