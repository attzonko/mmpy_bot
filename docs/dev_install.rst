Installation for development
============================

#. Clone repo and install requirements:

    .. code-block:: bash

        $ git clone https://github.com/attzonko/mmpy_bot.git
        $ cd mmpy_bot
        $ pip install -r requirements.txt
        $ pip install -r dev-requirements.txt

#. Spin up the Mattermost container (Podman or Docker required):

    .. code-block:: bash

        $ podman-compose -f tests/integration_tests/docker-compose.yml up -d

#. Edit mmpy_bot/settings.py and configure as below. If testing webhook
   server functionality, ensure **WEBHOOK_HOST_ENABLED** is set to `True`.

    .. code-block:: python

        MATTERMOST_URL: str = "http://127.0.0.1"
        MATTERMOST_PORT: int = 8065
        BOT_TOKEN: str = "e691u15hajdebcnqpfdceqihcc"
        BOT_TEAM: str = "test"
        SSL_VERIFY: bool = False
        WEBHOOK_HOST_ENABLED: bool = False
        WEBHOOK_HOST_URL: str = "http://127.0.0.1"
        WEBHOOK_HOST_PORT: int = 8579

#. Run the bot:

.. code-block:: python

    >>> from mmpy_bot.bot import Bot
    >>> Bot().run()
