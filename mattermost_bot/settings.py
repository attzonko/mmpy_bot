import importlib
import sys
import os

DEBUG = False

PLUGINS = [
    'mattermost_bot.plugins',
]
PLUGINS_ONLY_DOC_STRING = False

BOT_URL = 'http://mm.example.com/api/v1'
BOT_LOGIN = 'bot@example.com'
BOT_PASSWORD = None
BOT_TEAM = 'devops'

IGNORE_NOTIFIES = ['@channel', '@all']
WORKERS_NUM = 10

DEFAULT_REPLY_MODULE = None
DEFAULT_REPLY = None

'''
If you use Mattermost Web API to send messages (with send_webapi()
or reply_webapi()), you can customize the bot logo by providing Icon or Emoji.
If you use Mattermost API to send messages (with send() or reply()),
the used icon comes from bot settings and Icon or Emoji has no effect.
'''
# BOT_ICON = 'http://lorempixel.com/64/64/abstract/7/'
# BOT_EMOJI = ':godmode:'


for key in os.environ:
    if key[:15] == 'MATTERMOST_BOT_':
        globals()[key[11:]] = os.environ[key]

settings_module = os.environ.get('MATTERMOST_BOT_SETTINGS_MODULE')

if settings_module is not None:
    pwd = os.getcwd()
    if pwd not in sys.path:
        sys.path.insert(0, pwd)
    settings = importlib.import_module(settings_module)
    filename = settings.__file__.replace('.pyc', '.py')
    try:
        execfile(filename)
    except NameError:
        exec(open(filename).read())

try:
    from mattermost_bot_settings import *
except ImportError:
    try:
        from local_settings import *
    except ImportError:
        pass
