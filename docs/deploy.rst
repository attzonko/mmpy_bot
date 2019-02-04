Deploy
======

Ubuntu 14.04
------------

Install supervisor and virtualenv::

    $ sudo apt-get update
    $ sudo apt-get install supervisor python-virtualenv git


Add ``matterbot`` user::

    $ useradd --shell /bin/bash -m -d /home/matterbot matterbot


Login as ``matterbot``::

    sudo -i -u matterbot


Clone your project (before create git repository with ``settings.py``)::

    $ git clone https://github.com/USER/REPO.git ~/mybot


Create virtual environment::

    $ cd ~/
    $ virtualenv mm-env


Install project requirements::

    $ cd ~/mybot
    $ . ~/mm-env/bin/activate
    $ pip install mmpy_bot
    $ pip install -r requirements.txt


Logout::

    $ exit


Configure supervisor::

    $ sudo vi /etc/supervisor/conf.d/matterbot.conf

Add following config::

    [program:matterbot]
    command=/home/matterbot/mm-env/bin/mmpy_bot
    user=matterbot
    directory=/home/matterbot/mybot
    # should be a real settings file on MATTERMOST_BOT_SETTINGS_MODULE
    environment=MATTERMOST_BOT_SETTINGS_MODULE="settings"
    redirect_stderr=true
    stdout_logfile=/var/log/matterbot.log
    numprocs=1
    autostart=true
    autorestart=true
    startretries=25
    logfile_maxbytes=50MB
    logfile_backups=3
    killasgroup=true
    stopasgroup=true
    priority=998


Restart supervisor::

    $ service supervisor restart


Check status::

    $ supervisorctl status


Track bot logs::

    $ tail -f /var/log/matterbot.log


Enjoy:)
