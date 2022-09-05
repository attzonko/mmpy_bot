[![PyPI](https://badge.fury.io/py/mmpy-bot.svg)](https://pypi.org/project/mmpy-bot/)
[![Maintainability](https://api.codeclimate.com/v1/badges/809c8d66aea982d9e3da/maintainability)](https://codeclimate.com/github/attzonko/mmpy_bot/maintainability)
[![Python Support](https://img.shields.io/pypi/pyversions/mmpy-bot.svg)](https://pypi.org/project/mmpy-bot/)
[![Mattermost](https://img.shields.io/badge/mattermost-4.0+-blue.svg)](http://www.mattermost.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://pypi.org/project/mmpy-bot/)

Documentation available at [Read the Docs](https://mmpy-bot.readthedocs.org/).


## Description

A Python based chat bot framework for [Mattermost](http://www.mattermost.org). The code for
this bot framework was heavily re-factored in v2.0.0 and will only work with Python 3.8 or higher.
For Python 2 and Python3 < 3.8 support, please use versions v1.3.9 or lower.

## Features
- Based on Mattermost [WebSocket API(V4.0.0)](https://api.mattermost.com)
- Simple plugins mechanism
- Concurrent message handling
- Attachment support
- Auto-reconnect to Mattermost after connection loss

##### Additional features added in v2.x:
- Multi-threading and asyncio execution
- Integrated webhook server
- Support for click functions
- Job scheduling

## Compatibility

|    Mattermost    |  mmpy_bot   |
|------------------|:-----------:|
|     >= 4.0       |  > 1.2.0    |
|     <  4.0       | unsupported |


## Installation
:warning: Warning: pip will grab v1.x if your Python version is less than 3.8!

##### v2.x (latest)
```
pip install mmpy-bot
```

##### v1.3.9 (force legacy)
```
pip install mmpy-bot==1.3.9
```

## Usage (v2.x)

### Registration

First you need to create a bot account on your Mattermost server.
Note: **Enable Bot Account Creation** must be enabled under System Console
1. Login to your Mattermost server as a user with Administrative privileges.
1. Navigate to Integrations -> Bot Accounts -> Add Bot Account
1. Fill in the configuration options and upon creation take note of the **Access Token**

Note that some API functions, such as ephemeral message replies, will require the bot to be part of the **System Admin** group,
however most API functions will work with a regular **Member** account role. Just be aware that if some API functions are not working, it
may be due to a lack of appropriate permissions.


### Configure and run the bot

Create an entrypoint file (or copy the one provided), that defines your Mattermost server and bot account settings and imports
the desired modules.

Example `my_bot.py`:

```python
#!/usr/bin/env python

from mmpy_bot import Bot, Settings
from my_plugin import MyPlugin

bot = Bot(
    settings=Settings(
        MATTERMOST_URL = "http://chat.example.com",
        MATTERMOST_PORT = 443,
        MATTERMOST_API_PATH = '/api/v4',
        BOT_TOKEN = "a69155mvlsobcnqpfdceqihaa",
        BOT_TEAM = "test",
        SSL_VERIFY = True,
    ),  # Either specify your settings here or as environment variables.
    plugins=[MyPlugin()],  # Add your own plugins here.
)
bot.run()
```

Set the executable bit on the entrypoint file (i.e. `chmod +x my_bot.py`) and start your bot from the command prompt. Now you can talk to your bot in your Mattermost client!

In order to get the most out of your bot, you will need to write your own plugins. Refer to the [Plugins Documentation](https://mmpy-bot.readthedocs.io/en/latest/plugins.html) to get started.

### Talk to us

The primary channel for communication is [GitHub](https://github.com/attzonko/mmpy_bot)
via [Issues](https://github.com/attzonko/mmpy_bot/issues)
or [Pull requests](https://github.com/attzonko/mmpy_bot/pulls)
but you may also find some of us in [Discord](https://discord.gg/tWe5nVpNRB) for some real-time interaction.
