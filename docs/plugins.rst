Plugins
=======

A chat bot is meaningless unless you can extend/customize it to fit your own use cases, which can be achieved through custom plugins.

Writing your first plugin
-------------------------

#. To demonstrate how easy it is to create a plugin for `mmpy_bot`, let's write a basic plugin and run it. Start with an empty Python file and import these three `mmpy_bot` modules:

    .. code-block:: python

        from mmpy_bot import Plugin, listen_to
        from mmpy_bot import Message

#. Now create a Class with the name of your plugin, subclassing `Plugin`:

    .. code-block:: python

        class MyPlugin(Plugin):

#. Now we can write the methods that control how the bot will respond to certain messages. Let's start with a basic one that will simply trigger a response from the bot:

    .. code-block:: python

        @listen_to("wake up")
        async def wake_up(self, message: Message):
            self.driver.reply_to(message, "I'm awake!")

    In the above code block, the `@listen_to` decorator tells the bot to listen on any channel for the string "wake up", and respond with "I'm awake!".

#. Save your plugin file and open a fresh Python file which will be the entrypoint to start the bot and include your plugin:

    .. code-block:: python

        #!/usr/bin/env python

        from mmpy_bot import Bot, Settings
        from my_plugin import MyPlugin

        bot = Bot(
            settings=Settings(
                MATTERMOST_URL = "http://127.0.0.1",
                MATTERMOST_PORT = 8065,
                BOT_TOKEN = "<your_bot_token>",
                BOT_TEAM = "<team_name>",
                SSL_VERIFY = False,
            ),  # Either specify your settings here or as environment variables.
            plugins=[MyPlugin()],  # Add your own plugins here.
        )
        bot.run()

    The above code assumes your plugin is in the same directory as the entrypoint file. Also be sure to set the correct settings for your Mattermost server and bot account.

#. Save your entrypoint file and run it from the command prompt:

    .. code-block:: bash

        $ ./my_bot.py

If everything went as planned you can now start your bot, send the message "wake up" and expect the appropriate reply.

Further configuration
---------------------

The below code snippets provide an insight into the functionality that can be added to the bot. For more in-depth examples,
please refer to `./plugins/example.py <https://github.com/attzonko/mmpy_bot/blob/main/mmpy_bot/plugins/example.py>`_ and `./plugins/webhook_example.py <https://github.com/attzonko/mmpy_bot/blob/main/mmpy_bot/plugins/webhook_example.py>`_.

Implementing regular expression
-------------------------------

.. code-block:: python

    import re

    @listen_to('hi', re.IGNORECASE)
    def hi(message):
        message.reply('I can understand hi or HI!')

    @listen_to('Give me (.*)')
    async def give_me(self, message, something):
        self.driver.reply_to(message, 'Here is %s' % something)


Only accept messages that mention the bot
----------------------------------

If you want the bot to only respond to messages containing a mention (e.g. "hey @bot_name !"), you can use the `needs_mention` flag.
Note that this will also trigger if you send the bot a direct message without mentioning its name!
    .. code-block:: python

        @listen_to("hey", needs_mention=True)
        async def hey(self, message: Message):
            self.driver.reply_to(message, "Hi! You mentioned me?")


Only accept direct messages
----------------------------------

Using `direct_only=True`, the bot will only respond if you send it a direct message.

    .. code-block:: python

        @listen_to("hey", direct_only=True)
        async def hey(self, message: Message):
            self.driver.reply_to(message, "Hi! This is a private conversation.")


Restrict messages to specific users
----------------------------------

    .. code-block:: python

        @listen_to("^admin$", direct_only=True, allowed_users=["admin", "root"])
        async def users_access(self, message: Message):
            """Will only trigger if the username of the sender is 'admin' or 'root'."""
            self.driver.reply_to(message, "Access allowed!")


Restrict messages to specific channels
----------------------------------

    .. code-block:: python

        @listen_to("^poke$", allowed_channels=["#staff", "#town-square"])
        async def poke(self, message: Message):
            """Will only trigger if the message has been send in '#staff' or '#town-square'."""
            self.driver.reply_to(message, "Access allowed!")

Click support
-------------
    `mmpy_bot` now supports `click <https://click.palletsprojects.com/en/7.x/>`_ commands, so you can build a robust CLI-like experience if you need it.
    The example below registers a `hello_click` command that takes a positional argument, a keyword argument and a toggleable flag, which are automatically converted to the correct type.
    For example, it can be called with `hello_click my_argument --keyword-arg=3 -f` and will parse the arguments accordingly.
    A nice benefit of `click` commands is that they also automatically generate nicely formatted help strings.
    Try sending "help" to the `ExamplePlugin` to see what it looks like!

    .. code-block:: python

        @listen_to("hello_click", needs_mention=True)
        @click.command(help="An example click command with various arguments.")
        @click.argument("POSITIONAL_ARG", type=str)
        @click.option("--keyword-arg", type=float, default=5.0, help="A keyword arg.")
        @click.option("-f", "--flag", is_flag=True, help="Can be toggled.")
        def hello_click(
            self, message: Message, positional_arg: str, keyword_arg: float, flag: bool
        ):
            response = (
                "Received the following arguments:\n"
                f"- positional_arg: {positional_arg}\n"
                f"- keyword_arg: {keyword_arg}\n"
                f"- flag: {flag}\n"
            )
            self.driver.reply_to(message, response)

File upload
------------------

.. code-block:: python

    @listen_to("^hello_file$", re.IGNORECASE, needs_mention=True)
    async def hello_file(self, message: Message):
        """Responds by uploading a text file."""
        file = Path("/tmp/hello.txt")
        file.write_text("Hello from this file!")
        self.driver.reply_to(message, "Here you go", file_paths=[file])


Plugin startup and shutdown
---------------------------
The `Plugin` class comes with an `on_start` and `on_stop` function, which will be called when the bot starts up or shuts down.
They can be used as follows:

.. code-block:: python

    def on_start(self):
        """Notifies some channel that the bot is now running."""
        self.driver.create_post(channel_id="some_channel_id", message="The bot just started running!")

    def on_stop(self):
        """Notifies some channel that the bot is shutting down."""
        self.driver.create_post(channel_id="some_channel_id", message="I'll be right back!")


Webhook listener
---------------------
If you want to interact with your bot not only through chat messages but also through web requests (for example to implement an `interactive dialog <https://docs.mattermost.com/developer/interactive-dialogs.html>`_), you can use enable the built-in `WebHookServer`.
In your `Settings`, make sure to set `WEBHOOK_HOST_ENABLED=True` and provide a value for `WEBHOOK_HOST_URL` and `WEBHOOK_HOST_PORT` (see `settings.py <https://github.com/attzonko/mmpy_bot/blob/main/mmpy_bot/settings.py>`_ for more info).
Then, on your custom `Plugin` you can create a function like this:

.. code-block:: python

    from mmpy_bot import listen_webhook

    @listen_webhook("ping")
    async def ping_listener(self, event: WebHookEvent):
        """Listens to post requests to '<server_url>/hooks/ping' and posts a message in
        the channel specified in the request body."""

        self.driver.create_post(
            event.body["channel_id"], f"Webhook {event.webhook_id} triggered!"
        )

And if you want to send a web response back to the incoming HTTP POST request, you can use `Driver.respond_to_web`:

.. code-block:: python

    @listen_webhook("ping")
    async def ping_listener(self, event: WebHookEvent):
        # Respond to the web request rather than posting a message.
        self.driver.respond_to_web(
            event,
            {
                # You can add any kind of JSON-serializable data here
                "message": "hello!",
            },
        )

For more information about the `WebHookServer` and its possibilities, take a look at the `WebHookExample  plugin <https://github.com/attzonko/mmpy_bot/blob/main/mmpy_bot/plugins/webhook_example.py>`_.


Job scheduling
--------------

mmpy_bot integrates `schedule
<https://github.com/dbader/schedule/>`_ to provide in-process job scheduling.

With `schedule
<https://github.com/dbader/schedule/>`_, we can put periodic jobs into waiting queue like this:

.. code-block:: python

    @listen_to("^schedule every ([0-9]+)$", re.IGNORECASE, needs_mention=True)
    def schedule_every(self, message: Message, seconds: int):
        """Schedules a reply every x seconds. Use the `cancel jobs` command to stop.

        Arguments:
        - seconds (int): number of seconds between each reply.
        """
        schedule.every(int(seconds)).seconds.do(
            self.driver.reply_to, message, f"Scheduled message every {seconds} seconds!"
        )

    @listen_to('cancel jobs', re.IGNORECASE)
    def cancel_jobs(message):
        schedule.clear()
        self.driver.reply_to('All jobs cancelled.')

The `schedule
<https://github.com/dbader/schedule/>`_ package provides human-readable APIs to schedule jobs. Check out `schedule.readthedocs.io <https://schedule.readthedocs.io/>`_ for more usage examples.

`schedule
<https://github.com/dbader/schedule/>`_ is designed for periodic jobs.
In order to support one-time-only jobs, mmpy_bot has a monkey-patching on integrated
`schedule
<https://github.com/dbader/schedule/>`_ package.

We can schedule a one-time-only job by `schedule.once` method.
You should notice that this method takes a datetime object, which is different from `schedule.every` methods.

The following code example uses `schedule.once` to schedule a job.
This job will be trigger at `t_time`.
