Installation for development
============================

.. code-block:: bash

    $ sudo apt-get install virtualenvwrapper
    $ mkvirtualenv mattermost_bot
    $ git clone https://github.com/LPgenerator/mattermost_bot.git
    $ cd mattermost_bot
    $ python setup.py develop
    $ pip install -r requirements.txt
    $ pip install -r docs/requirements.txt
    $ touch local_settings.py               # configure your local settings
    $ matterbot                             # run bot


.. code-block:: python

    >>> import mattermost_bot
    >>> print(mattermost_bot.get_version())
