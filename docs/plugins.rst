Plugins
=======

A chat bot is meaningless unless you can extend/customize it to fit your own use cases, which can be achieved through custom plugins.

Writing your first plugin
-------------------------

#. First you need to create a Python file in the `./plugins` directory. For this example we will create the file ./plugins/my_plugin.py and
   import the required modules:

    .. code-block:: python

        from mmpy_bot.plugins.base import Plugin, listen_to
        from mmpy_bot.wrappers import Message


#. Next create a class with the name of your plugin and create an `asyncio` method with the `@listen_to` decorator:

    .. code-block:: python

        class MyPlugin(Plugin):

            @listen_to("wake up")
            async def wake_up(self, message: Message):
                self.driver.reply_to(message, "I'm awake!")

    In the above code block, the `@listen_to` decorator tells the bot to listen on any channel for the string "wake up", and respond with "I'm awake!".

#. Now open up `./plugins/__init__.py` and add your plugin module as follows:

    .. code-block:: python

        from mmpy_bot.plugins.base import Plugin
        from mmpy_bot.plugins.example import ExamplePlugin
        from mmpy_bot.plugins.webhook_example import WebHookExample
        from mmpy_bot.plugins.my_plugin import MyPlugin

        __all__ = ["Plugin", "ExamplePlugin", "WebHookExample", "MyPlugin"]

#. Last but not least, you will need to ensure your plugin is started by the bot. In this example we will update the default `bot.py` file
   to import `MyPlugin`:

    .. code-block:: python

        from mmpy_bot.plugins import ExamplePlugin, Plugin, WebHookExample, MyPlugin

        def __init__(self, settings=Settings(), plugins=[ExamplePlugin(), WebHookExample(),
                     MyPlugin()]
        ):

   If everything went as planned you can now start your bot, send the message "wake up" and expect to appropriate reply.

Further configuration
---------------------

The below code snippets provide an insight into the functionality that can be added to the bot. For more in-depth examples,
please refer to `./plugins/example.py` and `./plugins/webhook_example.py`.

Implementing regular expression
-------------------------------

.. code-block:: python

    import re

    @listen_to('hi', re.IGNORECASE)
    def hi(message):
        message.reply('I can understand hi or HI!')

    @listen_to('Give me (.*)')
    def give_me(message, something):
        message.reply('Here is %s' % something)

Restrict messages to specific users
----------------------------------

    .. code-block:: python

        @listen_to("^admin$", direct_only=True, allowed_users=["admin", "root"])
        async def users_access(self, message: Message):
            """Showcases a function with restricted access."""
            self.driver.reply_to(message, "Access allowed!")

Click support
-------------

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

Job scheduling
--------------

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

