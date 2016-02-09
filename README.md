[![PyPI](https://badge.fury.io/py/mattermost_bot.svg)](https://pypi.python.org/pypi/mattermost_bot)

A chat bot for [mattermost](http://www.mattermost.org).

## Features

* Based on MatterMost [WebSocket API](https://github.com/mattermost/platform)
* Simple plugins mechanism
* Messages can be handled concurrently
* Automatically reconnect to mattermost when connection is lost
* Python3 Support

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
BOT_URL = '<http://mm.example.com/api/v1>'  # with 'http://' and with '/api/v1' path
BOT_LOGIN = '<bot-email-address>'
BOT_PASSWORD = '<bot-password>'
BOT_TEAM = '<your-team>'
```

Alternatively, you can use the environment variable `MATTERMOST_BOT_URL`,
`MATTERMOST_BOT_LOGIN`, `MATTERMOST_BOT_PASSWORD`, `MATTERMOST_BOT_TEAM`.

### Run the bot

```python
from mattermost_bot.bot import Bot

if __name__ == "__main__":
    Bot().run()
```

Now you can talk to your bot in your mattermost client!

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
def help(message):
    # Message is replied to the sender (prefixed with @user)
    message.reply('Yes, I can!')

    # Message is sent on the channel
    # message.send('I can help everybody!')
```

To extract params from the message, you can use regular expression:
```python
from mattermost_bot.bot import respond_to


@respond_to('Give me (.*)')
def giveme(message, something):
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
    'mybot.plugins',
]
```

Source based on [SlackBot](https://github.com/lins05/slackbot).
