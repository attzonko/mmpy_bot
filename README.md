[![PyPI](https://badge.fury.io/py/mattermost_bot.svg)](https://pypi.python.org/pypi/mattermost_bot)
[![Codacy](https://api.codacy.com/project/badge/grade/b06f3af1d8a04c6faa9a76a4ae3cb483)](https://www.codacy.com/app/gotlium/mattermost_bot)
[![Code Health](https://landscape.io/github/LPgenerator/mattermost_bot/master/landscape.svg?style=flat)](https://landscape.io/github/LPgenerator/mattermost_bot/master)
[![Downloads from PyPi](https://img.shields.io/pypi/dm/mattermost_bot.svg)](https://pypi.python.org/pypi/mattermost_bot/)
[![Python Support](https://img.shields.io/badge/python-2.7,3.5-blue.svg)](https://pypi.python.org/pypi/mattermost_bot/)
[![Mattermost](https://img.shields.io/badge/mattermost-1.4+-blue.svg)](http://www.mattermost.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://pypi.python.org/pypi/mattermost_bot/)

Documentation available at [Read the Docs](http://mattermost-bot.readthedocs.org/).


## What's that

A chat bot for [Mattermost](http://www.mattermost.org).

## Features

* Based on MatterMost [WebSocket API](https://github.com/mattermost/platform)
* Simple plugins mechanism
* Messages can be handled concurrently
* Automatically reconnect to mattermost when connection is lost
* Python3 Support
* Mattermost >= 3.0 (for versions < 3.0, please use app version <= 1.0.15)

## Installation

```
pip install mattermost_bot
```

## Usage

### Registration

First you need create the mattermost email/password for your bot.

### Configuration

Then you need to configure the `BOT_URL`, `BOT_LOGIN`, `BOT_PASSWORD`, `BOT_TEAM` in a python module
`mattermost_bot_settings.py`, which must be located in a python import path.


mattermost_bot_settings.py:

```python
BOT_URL = 'http://<mm.example.com>/api/v3'  # with 'http://' and with '/api/v3' path. without trailing slash. '/api/v1' - for version < 3.0
BOT_LOGIN = '<bot-email-address>'
BOT_PASSWORD = '<bot-password>'
BOT_TEAM = '<your-team>'  # possible in lowercase
```

Alternatively, you can use the environment variable `MATTERMOST_BOT_URL`,
`MATTERMOST_BOT_LOGIN`, `MATTERMOST_BOT_PASSWORD`, `MATTERMOST_BOT_TEAM`.

or `MATTERMOST_BOT_SETTINGS_MODULE` environment variable, which provide settings module

```bash
MATTERMOST_BOT_SETTINGS_MODULE=settings.bot_conf matterbot
```


### Run the bot

Use the built-in cli script and point to your custom settings file.

```bash
MATTERMOST_BOT_SETTINGS_MODULE=mattermost_bot_settings matterbot
```

or you can create your own startup file. For example `run.py`:

```python
from mattermost_bot.bot import Bot


if __name__ == "__main__":
    Bot().run()
```

Now you can talk to your bot in your mattermost client!



## Attachment Support

```python
from mattermost_bot.bot import respond_to


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
```

*Integrations must be allowed for non admins users.*

## Plugins

A chat bot is meaningless unless you can extend/customize it to fit your own use cases.

To write a new plugin, simply create a function decorated by `mattermost_bot.bot.respond_to` or `mattermost_bot.bot.listen_to`:

- A function decorated with `respond_to` is called when a message matching the pattern is sent to the bot (direct message or @botname in a channel/group chat)
- A function decorated with `listen_to` is called when a message matching the pattern is sent on a channel/group chat (not directly sent to the bot)

```python
import re

from mattermost_bot.bot import listen_to
from mattermost_bot.bot import respond_to


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
```

To extract params from the message, you can use regular expression:
```python
from mattermost_bot.bot import respond_to


@respond_to('Give me (.*)')
def give_me(message, something):
    message.reply('Here is %s' % something)
```

If you would like to have a command like 'stats' and 'stats start_date end_date', you can create reg ex like so:

```python
from mattermost_bot.bot import respond_to
import re


@respond_to('stat$', re.IGNORECASE)
@respond_to('stat (.*) (.*)', re.IGNORECASE)
def stats(message, start_date=None, end_date=None):
    pass
```


And add the plugins module to `PLUGINS` list of mattermost_bot settings, e.g. mattermost_bot_settings.py:

```python
PLUGINS = [
    'mattermost_bot.plugins',
    'devops.plugins',          # e.g. git submodule:  domain:devops-plugins.git
    'programmers.plugins',     # e.g. python package: package_name.plugins
    'frontend.plugins',        # e.g. project tree:   apps.bot.plugins
]
```
*For example you can separate git repositories with plugins on your team.*


If you are migrating from `Slack` to the `Mattermost`, and previously you are used `SlackBot`,
you can use this battery without any problem. On most cases your plugins will be working properly
if you are used standard API or with minimal modifications.
