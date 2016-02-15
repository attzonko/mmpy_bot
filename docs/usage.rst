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


Integration with Django
-----------------------

Create bot_settings on your project and after you can create `django` command::

    import logging
    import sys

    from django.core.management.base import BaseCommand
    from django.conf import settings

    from mattermost_bot import bot, settings


    class Command(BaseCommand):

        def handle(self, **options):

            logging.basicConfig(**{
                'format': '[%(asctime)s] %(message)s',
                'datefmt': '%m/%d/%Y %H:%M:%S',
                'level': logging.DEBUG if settings.DEBUG else logging.INFO,
                'stream': sys.stdout,
            })

            try:
                b = bot.Bot()
                b.run()
            except KeyboardInterrupt:
                pass


Modify `manage.py`::

    #!/usr/bin/env python
    import os
    import sys

    if __name__ == "__main__":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
        os.environ.setdefault("MATTERMOST_BOT_SETTINGS_MODULE", "project.bot_settings")

        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv)
