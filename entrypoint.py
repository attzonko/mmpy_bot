from mmpy_bot import Bot, ExamplePlugin, Settings, WebHookExample

bot = Bot(
    # Either specify your settings here or use environment variables to override them.
    # See docker-compose.yml for an example you can use for local development.
    settings=Settings(),
    plugins=[ExamplePlugin(), WebHookExample()],  # Add your own plugins here.
)
bot.run()
