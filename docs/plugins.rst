Plugins
=======


Plugins
-------

A chat bot is meaningless unless you can extend/customize it to fit your own use cases.

To write a new plugin, simply create a function decorated by ``mmpy_bot.bot.respond_to`` or ``mmpy_bot.bot.listen_to``:

- A function decorated with ``respond_to`` is called when a message matching the pattern is sent to the bot (direct message or @botname in a channel/group chat)
- A function decorated with ``listen_to`` is called when a message matching the pattern is sent on a channel/group chat (not directly sent to the bot)
- A function decorated with ``at_start`` is called as soon as the plugin is initialized (when the bot starts)

.. code-block:: python

    import re

    from mmpy_bot.bot import listen_to
    from mmpy_bot.bot import respond_to


    @respond_to('hi', re.IGNORECASE)
    def hi(message):
        message.reply('I can understand hi or HI!')


    @respond_to('I love you')
    def love(message):
        message.reply('I love you too!')


    @listen_to('Can someone help me?')
    def help_me(message):
        # Message is replied to the sender (prefixed with @user)
        message.reply('Yes, I can!')

        # Message is sent on the channel
        # message.send('I can help everybody!')

    @at_start
    def hello(client):
        # Note that contrary to respond_to and listen_to @at_start
        # receives a client object and not a message object
        team = client.api.get_team_by_name("TESTTEAM")
        channel = client.api.get_channel_by_name("bot_test", team["id"])
        client.channel_msg(channel["id"], "Hello, feels good to be alive!!")

To extract params from the message, you can use regular expression:

.. code-block:: python

    from mmpy_bot.bot import respond_to


    @respond_to('Give me (.*)')
    def give_me(message, something):
        message.reply('Here is %s' % something)


If you would like to have a command like 'stats' and 'stats start_date end_date', you can create reg ex like so:

.. code-block:: python

    from mmpy_bot.bot import respond_to
    import re


    @respond_to('stat$', re.IGNORECASE)
    @respond_to('stat (.*) (.*)', re.IGNORECASE)
    def stats(message, start_date=None, end_date=None):
        pass



And add the plugins module to ``PLUGINS`` list of mmpy_bot settings, e.g. ``mmpy_bot_settings.py``:

.. code-block:: python

    PLUGINS = [
        'mmpy_bot.plugins',
        'devops.plugins',          # e.g. git submodule: domain:devops-plugins.git
        'programmers.plugins',     # e.g. python package: package_name.plugins
        'frontend.plugins',        # e.g. project tree: apps.bot.plugins
    ]

*For example you can separate git repositories with plugins on your team.*


Attachment Support
------------------

.. code-block:: python

    from mmpy_bot.bot import respond_to


    @respond_to('webapi')
    def webapi_reply(message):
        attachments = [{
            'fallback': 'Fallback text',
            'author_name': 'Author',
            'author_link': 'http://www.github.com',
            'text': 'Some text here ...',
            'color': '#59afe1'
        }]
        message.reply_webapi(
            'Attachments example', attachments,
            username='Mattermost-Bot',
            icon_url='https://goo.gl/OF4DBq',
        )
        # Optional: Send message to specified channel
        # message.send_webapi('', attachments, channel_id=message.channel)


File Support
------------------

.. code-block:: python

    from mmpy_bot.bot import respond_to


    @respond_to('files')
    def message_with_file(message):
        # upload_file() can upload only one file at a time
        # If you have several files to upload, you need call this function several times.
        file = open('test.txt', 'w+')
        result = message.upload_file(file)
        file.close()
        if 'file_infos' not in result:
            message.reply('upload file error')
        file_id = result['file_infos'][0]['id']
        # file_id need convert to array
        message.reply('hello', [file_id])


Webhook Support
------------------

You can specify ``webhook_id`` at ``reply_webapi`` and ``send_webapi`` method call.
The ``webhook_id`` can be generated and acquired from Mattermost Contol Panel.
It is also possible to send messages to different teams/channels in the same message handler, as long as you got needed webhook_ids.

.. code-block:: python

    from mmpy_bot.bot import respond_to

    @respond_to('reply')
    def reply(message):
        attachments = [{
            'fallback': 'Fallback text',
            'author_name': 'Author',
            'author_link': 'http://www.github.com',
            'text': 'Some text here ...',
            'color': '#59afe1'
        }]
        message.reply_webapi(
            'Response to team I got message from.',
            attachments,
            webhook_id='p7tuwghy37r63jp4nf3tsopque',
        )
        # Optional: Send message to specified channel
        message.send_webapi(
            'Response to another team.',
            attachments,
            webhook_id='aib7mnahsfy5zrt6tf3ycbghic',
        )

You can also set ``WEBHOOK_ID`` in settings.py or local_settings.py.
The ``WEBHOOK_ID`` will serve as default webhook id to send message via webhook API if ``webhook_id`` is not given at ``reply_webapi`` or ``send_webapi`` method call.

.. code-block:: python

    import os

    PLUGINS = [
        'my_plugins',
    ]

    BOT_URL = os.environ.get("BOT_URL", 'http://your_server_dn/api/v4')
    BOT_LOGIN = os.environ.get("DRIVERBOT_LOGIN", 'bot@nature.ee.ncku.edu.tw')
    BOT_NAME = os.environ.get("DRIVERBOT_NAME", 'bot')
    BOT_PASSWORD = os.environ.get("DRIVERBOT_PASSWORD", 'passwd')

    # this team name should be the same as in driver_settings
    BOT_TEAM = os.environ.get("BOT_TEAM", 'test_team')

    # default public channel name
    BOT_CHANNEL = os.environ.get("BOT_CHANNEL", 'off-topic')

    # a private channel in BOT_TEAM
    BOT_PRIVATE_CHANNEL = os.environ.get("BOT_PRIVATE_CHANNEL", 'test')

    SSL_VERIFY = True

    # example webhook_id of test_team/off-topic
    WEBHOOK_ID = 'p7tuwghy37r63jp4nf3tsopque'

If neither ``webhook_id`` (as parameter) nor ``WEBHOOK_ID`` (in settings.py) is given, the message will not be send, and a warning will be added to logging.


Job Scheduling
--------------

mmpy_bot integrates `schedule 
<https://github.com/dbader/schedule/>`_ to provide in-process job scheduling.

With `schedule 
<https://github.com/dbader/schedule/>`_, we can put periodic jobs into waiting queue like this:

.. code-block:: python

    import re
    from datetime import datetime
    from mmpy_bot.bot import respond_to
    from mmpy_bot.scheduler import schedule


    @respond_to('reply \"(.*)\" every (.*) seconds', re.IGNORECASE)
    def reply_every_seconds(message, content, seconds):
        schedule.every(int(seconds)).seconds.do(message.reply, content)


    @respond_to('cancel jobs', re.IGNORECASE)
    def cancel_jobs(message):
        schedule.clear()
        message.reply('all jobs canceled.')

The `schedule 
<https://github.com/dbader/schedule/>`_ itself provide human-readable APIs to schedule jobs. Check out `schedule.readthedocs.io <https://schedule.readthedocs.io/>`_ for more usage examples.

`schedule 
<https://github.com/dbader/schedule/>`_ is designed for periodic jobs.
In order to support one-time-only jobs, mmpy_bot has a monkey-patching on integrated 
`schedule 
<https://github.com/dbader/schedule/>`_ package.

We can schedule a one-time-only job by `schedule.once` method.
You should notice that this method takes a datetime object, which is different from `schedule.every` methods.

The following code example uses `schedule.once` to schedule a job.
This job will be trigger at `t_time`.

.. code-block:: python

    import re
    from datetime import datetime
    from mmpy_bot.bot import respond_to
    from mmpy_bot.scheduler import schedule


    @respond_to('reply \"(.*)\" at (.*)', re.IGNORECASE)
    def reply_specific_time(message, content, trigger_time):
        t_time = datetime.strptime(trigger_time, '%b-%d-%Y_%H:%M:%S')
        schedule.once(t_time).do(message.reply, content)

All jobs added will be triggered periodically. 
The trigger period (default 5 seconds) can be configured by `JOB_TRIGGER_PERIOD` in settings.py or local_settings.py.
