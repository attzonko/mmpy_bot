[![PyPI](https://badge.fury.io/py/mmpy_bot.svg)](https://pypi.python.org/pypi/mmpy_bot)
[![Codacy](https://api.codacy.com/project/badge/grade/b06f3af1d8a04c6faa9a76a4ae3cb483)](https://www.codacy.com/app/attzonko/mmpy_bot)
[![Code Health](https://landscape.io/github/LPgenerator/mmpy_bot/master/landscape.svg?style=flat)](https://landscape.io/github/LPgenerator/mattermost_bot/master)
[![Python Support](https://img.shields.io/badge/python-2.7,3.5-blue.svg)](https://pypi.python.org/pypi/mmpy_bot/)
[![Mattermost](https://img.shields.io/badge/mattermost-1.4+-blue.svg)](http://www.mattermost.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://pypi.python.org/pypi/mmpy_bot/)

Documentation available at [Read the Docs](http://mmpy_bot.readthedocs.org/).


## What is This

A python based chat bot for [Mattermost](http://www.mattermost.org).

## Features

* Based on Mattermost [WebSocket API(V4.0.0)](https://api.mattermost.com)
* Simple plugins mechanism
* Messages can be handled concurrently
* Automatically reconnect to Mattermost when connection is lost
* Python3 Support


## Compatibility

|    Mattermost    |  mmpy_bot   |
|------------------|:-----------:|
|     >= 4.0       |  > 1.0.0    |
|     <  4.0       | unsupported |


## Installation

```
pip install mmpy_bot
```

## Usage

### Registration

First you need create the mattermost email/password for your bot.

### Configuration

Then you need to configure the `BOT_URL`, `BOT_LOGIN`, `BOT_PASSWORD`, `BOT_TEAM` in a python module
`mmpy_bot_settings.py`, which must be located in a python import path.


mmpy_bot_settings.py:

```python
SSL_VERIFY = True  # Whether to perform SSL cert verification
BOT_URL = 'http://<mm.example.com>/api/v3'  # with 'http://' and with '/api/v3' path. without trailing slash. '/api/v1' - for version < 3.0
BOT_LOGIN = '<bot-email-address>'
BOT_PASSWORD = '<bot-password>'
BOT_TEAM = '<your-team>'  # possible in lowercase
```

Alternatively, you can use the environment variable `MATTERMOST_BOT_URL`,
`MATTERMOST_BOT_LOGIN`, `MATTERMOST_BOT_PASSWORD`, `MATTERMOST_BOT_TEAM`,
`MATTERMOST_BOT_SSL_VERIFY`

or `MATTERMOST_BOT_SETTINGS_MODULE` environment variable, which provide settings module

```bash
MATTERMOST_BOT_SETTINGS_MODULE=settings.bot_conf matterbot
```


### Run the bot

Use the built-in cli script and point to your custom settings file.

```bash
MATTERMOST_BOT_SETTINGS_MODULE=mmpy_bot_settings matterbot
```

or you can create your own startup file. For example `run.py`:

```python
from mmpy_bot.bot import Bot


if __name__ == "__main__":
    Bot().run()
```

Now you can talk to your bot in your mattermost client!



## Attachment Support

```python
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
```

*Integrations must be allowed for non admins users.*

## Plugins

A chat bot is meaningless unless you can extend/customize it to fit your own use cases.

To write a new plugin, simply create a function decorated by `mmpy_bot.bot.respond_to` or `mmpy_bot.bot.listen_to`:

- A function decorated with `respond_to` is called when a message matching the pattern is sent to the bot (direct message or @botname in a channel/group chat)
- A function decorated with `listen_to` is called when a message matching the pattern is sent on a channel/group chat (not directly sent to the bot)

```python
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
```

To extract params from the message, you can use regular expression:
```python
from mmpy_bot.bot import respond_to


@respond_to('Give me (.*)')
def give_me(message, something):
    message.reply('Here is %s' % something)
```

If you would like to have a command like 'stats' and 'stats start_date end_date', you can create reg ex like so:

```python
from mmpy_bot.bot import respond_to
import re


@respond_to('stat$', re.IGNORECASE)
@respond_to('stat (.*) (.*)', re.IGNORECASE)
def stats(message, start_date=None, end_date=None):
    pass
```


And add the plugins module to `PLUGINS` list of mmpy_bot settings, e.g. mmpy_bot_settings.py:

```python
PLUGINS = [
    'mmpy_bot.plugins',
    'devops.plugins',          # e.g. git submodule:  domain:devops-plugins.git
    'programmers.plugins',     # e.g. python package: package_name.plugins
    'frontend.plugins',        # e.g. project tree:   apps.bot.plugins
]
```
*For example you can separate git repositories with plugins on your team.*


If you are migrating from `Slack` to the `Mattermost`, and previously you are used `SlackBot`,
you can use this battery without any problem. On most cases your plugins will be working properly
if you are used standard API or with minimal modifications.

## Run the tests

You will need a Mattermost server to run test cases. 

 * Create two user accounts for bots to login, ex. `driverbot` and `testbot`
 * Create a team, ex. `test-team`, and add `driverbot` and `testbot` into the team
 * Make sure the default public channel `off-topic` exists
 * Create a private channel (ex. `test`) in team `test-team`, and add `driverbot` and `testbot` into the private channel

Install `PyTest` in development environment.

```
pip install -U pytest
```

There are two test categories in `mmpy_bot\tests`: __unit_tests__ and __behavior_tests__. The __behavior_tests__ is done by interactions between a __DriverBot__ and a __TestBot__.

To run the __behavior_tests__, you have to configure `behavior_tests\bot_settings.py` and `behavior_tests\driver_settings.py`. Example configuration:

__driver_settings.py__:
```python
PLUGINS = [
]

BOT_URL = 'http://mymattermost.server/api/v4'
BOT_LOGIN = 'driverbot@mymail'
BOT_NAME = 'driverbot'
BOT_PASSWORD = 'password'
BOT_TEAM = 'test-team'  # this team name should be the same as in bot_settings
BOT_CHANNEL = 'off-topic' # default public channel name
BOT_PRIVATE_CHANNEL = 'test' # a private channel in BOT_TEAM
SSL_VERIFY = True
```

__bot_settings.py__:
```python
PLUGINS = [
]

BOT_URL = 'http://mymattermost.server/api/v4'
BOT_LOGIN = 'testbot@mymail'
BOT_NAME = 'testbot'
BOT_PASSWORD = 'password'
BOT_TEAM = 'test-team'  # this team name should be the same as in driver_settings
BOT_CHANNEL = 'off-topic'   # default public channel name
BOT_PRIVATE_CHANNEL = 'test' # a private channel in BOT_TEAM
SSL_VERIFY = True
```

Please notice that `BOT_URL`, `BOT_TEAM`, `BOT_CHANNEL`, and `BOT_PRIVATE_CHANNEL` must be the same in both setting files.

After the settings files are done, switch to root dir of mattermost, and run `pytest` to execute test cases.
