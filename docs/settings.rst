.. _settings:

Settings
========

``mattermost_bot`` has some configuration:

.. code-block:: python

    DEBUG = False

    PLUGINS = [
        'mattermost_bot.plugins',
    ]

    # Docs + regexp or docs string only
    PLUGINS_ONLY_DOC_STRING = False

    # Basic configuration
    BOT_URL = 'http://mm.example.com/api/v1'
    BOT_LOGIN = 'bot@example.com'
    BOT_PASSWORD = None
    BOT_TEAM = 'devops'

    # Ignore broadcast message
    IGNORE_NOTIFIES = ['@channel', '@all']

    # Threads num
    WORKERS_NUM = 10

    # You can specify you custom module
    DEFAULT_REPLY_MODULE = None
