import os

DEBUG = False

PLUGINS = [
    'mattermost_bot.plugins',
]

BOT_URL = 'http://mm.example.com/api/v1'
BOT_LOGIN = 'bot@example.com'
BOT_PASSWORD = 'XXX'
BOT_TEAM = 'devops'

for key in os.environ:
    if key[:15] == 'MATTERMOST_BOT_':
        globals()[key[11:]] = os.environ[key]

try:
    from mattermost_bot_settings import *
except ImportError:
    try:
        from local_settings import *
    except ImportError:
        pass
