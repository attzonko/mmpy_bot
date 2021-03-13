from mmpy_bot import Bot, ExamplePlugin, Settings, WebHookExample

bot = Bot(
    settings=Settings(),  # Either specify your settings here or as environment variables.
    plugins=[ExamplePlugin(), WebHookExample()],  # Add your own plugins here.
)
bot.run()
