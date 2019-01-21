Installation for development
============================

.. code-block:: bash

    $ sudo apt-get install virtualenvwrapper
    $ mkvirtualenv mmpy_bot
    $ git clone https://github.com/attzonko/mmpy_bot.git
    $ cd mmpy_bot
    $ python setup.py develop
    $ pip install -r requirements.txt
    $ pip install -r docs/requirements.txt
    $ touch local_settings.py               # configure your local settings
    $ mmpy_bot                              # run bot


.. code-block:: python

    >>> import mmpy_bot
    >>> print(mmpy_bot.get_version())
