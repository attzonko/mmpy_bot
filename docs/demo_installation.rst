Demo installation
=================

Install OS specific packages::

    # Ubuntu
    sudo apt-get install python-virtualenv python-pip

    # CentOS
    sudo yum install python-virtualenv python-pip

    # OS X
    brew install python

Create project directory and virtual environment::

    mkdir ~/my-bot && cd ~/my-bot
    virtualenv venv
    . venv/bin/activate

Install stable package from PyPi::

    pip install mmpy_bot

Create settings file `mmpy_bot_settings.py` with the following lines::

    DEBUG = True
    BOT_URL = 'http://mm.example.com:8065/api/v4'
    BOT_LOGIN = '<BOT_EMAIL>'
    BOT_PASSWORD = '<BOT_PASSWORD>'
    BOT_TEAM = '<TEAM>'

Run your bot by following command::

    MATTERMOST_BOT_SETTINGS_MODULE=mmpy_bot_settings mmpy_bot
