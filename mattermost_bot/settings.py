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

for key in os.environ:
    if key[:15] == 'MATTERMOST_BOT_':
        globals()[key[11:]] = os.environ[key]

settings_module = os.environ.get('MATTERMOST_BOT_SETTINGS_MODULE')

if settings_module is not None:
    pwd = os.getcwd()
    if pwd not in sys.path:
        sys.path.insert(0, pwd)
    settings = importlib.import_module(settings_module)
    execfile(settings.__file__.replace('.pyc', '.py'))

try:
    from mattermost_bot_settings import *
except ImportError:
    try:
        from local_settings import *
    except ImportError:
        pass

if not BOT_URL.endswith('/api/v1'):
    BOT_URL = '%s%sapi/v1' % (BOT_URL, '' if BOT_URL.endswith('/') else '/')
