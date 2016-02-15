Usage
=====

.. _basic:

Basic
-----

Register new user on Mattermost. Copy email/password/team and url into `settings.py` file::

    BOT_URL = 'http://<mm.example.com>/api/v1'  # with 'http://' and with '/api/v1' path
    BOT_LOGIN = '<bot-email-address>'
    BOT_PASSWORD = '<bot-password>'
    BOT_TEAM = '<your-team>'



Run the bot::

    $ MATTERMOST_BOT_SETTINGS_MODULE=settings matterbot

