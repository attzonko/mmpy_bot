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

    '''
    # Custom default reply module

    Example:
    filename:
        my_default_reply.py
    code:
        def default_reply(dispatcher, raw_msg):
            dispatcher._client.channel_msg(
                raw_msg['channel_id'], dispatcher.get_message(raw_msg)
            )
    settings:
        DEFAULT_REPLY_MODULE = 'my_default_reply'
    '''
    DEFAULT_REPLY_MODULE = None

    # or simple string for default answer
    DEFAULT_REPLY = None

    '''
    If you use Mattermost Web API to send messages (with send_webapi()
    or reply_webapi()), you can customize the bot logo by providing Icon or Emoji.
    If you use Mattermost API to send messages (with send() or reply()),
    the used icon comes from bot settings and Icon or Emoji has no effect.
    '''
    BOT_ICON = 'http://lorempixel.com/64/64/abstract/7/'
    BOT_EMOJI = ':godmode:'
