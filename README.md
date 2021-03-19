[![PyPI](https://badge.fury.io/py/mmpy-bot.svg)](https://pypi.org/project/mmpy-bot/)
[![Travis-Ci](https://travis-ci.com/attzonko/mmpy_bot.svg?branch=master)](https://travis-ci.com/attzonko/mmpy_bot)
[![Codacy](https://api.codacy.com/project/badge/grade/b06f3af1d8a04c6faa9a76a4ae3cb483)](https://www.codacy.com/app/attzonko/mmpy_bot)
[![Maintainability](https://api.codeclimate.com/v1/badges/809c8d66aea982d9e3da/maintainability)](https://codeclimate.com/github/attzonko/mmpy_bot/maintainability)
[![Python Support](https://img.shields.io/pypi/pyversions/mmpy-bot.svg)](https://pypi.org/project/mmpy-bot/)
[![Mattermost](https://img.shields.io/badge/mattermost-4.0+-blue.svg)](http://www.mattermost.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://pypi.org/project/mmpy-bot/)

Documentation available at [Read the Docs](http://mmpy_bot.readthedocs.org/).


## Description

A Python based chat bot for [Mattermost](http://www.mattermost.org). The code for
this bot was heavily re-factored in v2.0.0 and will only work with Python 3.8 or higher.
For Python 2 support, please use v1.3.9 or lower.

## Features

- [x] Based on Mattermost [WebSocket API(V4.0.0)](https://api.mattermost.com)
- [x] Simple plugins mechanism
- [x] Concurrent message handling
- [x] Attachment support
- [x] Auto-reconnect to Mattermost after connection loss
- [x] Python 2 compatible (<=v1.3.9 only)

##### Additional features in v2.0.0:
- [x] Multi-threading and asyncio execution
- [x] Integrated webhook server
- [x] Support for click functions
- [x] Job scheduling
- [x] Compatible with Python 3.8+ only


## Compatibility

|    Mattermost    |  mmpy_bot   |
|------------------|:-----------:|
|     >= 4.0       |  > 1.2.0    |
|     <  4.0       | unsupported |


## Installation

##### v2.0.0 refactor
```
pip install mmpy_bot
```

##### v1.3.9 legacy
```
pip install mmpy_bot==1.3.9
```

## Usage (v2.0.0)

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
