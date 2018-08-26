Plugins
=======


Plugins
-------

A chat bot is meaningless unless you can extend/customize it to fit your own use cases.

To write a new plugin, simply create a function decorated by ``mmpy_bot.bot.respond_to`` or ``mmpy_bot.bot.listen_to``:

- A function decorated with ``respond_to`` is called when a message matching the pattern is sent to the bot (direct message or @botname in a channel/group chat)
- A function decorated with ``listen_to`` is called when a message matching the pattern is sent on a channel/group chat (not directly sent to the bot)

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
