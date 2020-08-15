.. _decorators:

Built-in decorators
===================


Allowed users:

.. code-block:: python

    from mmpy_bot.utils import allowed_users
    from mmpy_bot.bot import respond_to


    @respond_to('^is-allowed$')
    @allowed_users('admin', 'root', 'root@admin.com')
    def access_allowed(message):
        message.reply('Access is allowed')



Direct messages:

.. code-block:: python

    from mmpy_bot.utils import allow_only_direct_message
    from mmpy_bot.bot import respond_to


    @respond_to('^direct-msg$')
    @allow_only_direct_message()
    def direct_msg(message):
        message.reply('Message is direct')



Actions just after plugin initilization:

.. code-block:: python

    from mmpy_bot.bot import at_start


    @at_start
    def hello(client):
        client.connect_websocket()
        client.ping()


Real case
---------

For example we have some users on our chat. We want allow some functionality
to some users. We can create constants with allowed users on bot settings:

.. code-block:: python

    ADMIN_USERS = ['admin', 'root', 'root@admin.com']
    SUPPORT_USERS = ['mike', 'nick', 'nick@nick-server.com']


So now we can close access to some functions on plugins:

.. code-block:: python

    from mmpy_bot.utils import allow_only_direct_message
    from mmpy_bot.utils import allowed_users
    from mmpy_bot.bot import respond_to
    from mmpy_bot import settings


    @respond_to('^selfupdate')
    @allow_only_direct_message()
    @allowed_users(*settings.ADMIN_USERS)
    def self_update(message):
        # some code
        message.reply('Update was done')


    @respond_to('^smsto (.*)')
    @allowed_users(*settings.SUPPORT_USERS)
    def sms_to(message, name):
        # some code
        message.reply('Sms was sent to %s' % name)


    @at_start
    def hello(client):
        team = client.api.get_team_by_name("TESTTEAM")
        channel = client.api.get_channel_by_name("bot_test", team["id"])
        client.channel_msg(channel["id"], "Hello, feels good to be alive!!")
