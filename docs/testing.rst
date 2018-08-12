.. _testing:


Testing
=======

mmpy_bot develops all tests based on pytest. If you need to add your own tests and run tests, please install pytest first.

.. code-block:: bash

	$ pip install -U pytest

All the tests are put in `mmpy_bot\tests`.
There are two test packages: :code:`unit_tests` and :code:`behavior_tests`.

Tests which can be performed by a single bot without mattermost server or other bots should be kept in :code:`unit_tests` package.
Other tests requiring interactions between bots on mattermost server belong to :code:`behavior_tests` package.


Add unit tests
--------------

There are multiple test modules inside unit_tests package.
Each module collects tests of specific mmpy_bot class or module.
The naming convention of these modules is *test_classname* or *test_modulename*.
Inside each module, there will be several test functions with naming convention *test_functionname* or *test_methodname*.
Each test function performs unit test against a specific class or module.
If you need to add more unit tests, please consider following these conventions.


Run unit tests
--------------

To run unit tests, simply:

.. code-block:: bash

	$ pytest tests\unit_tests


Add behavior tests
------------------

The behavior tests are done by interactions between a DriverBot (driver) and a TestBot (responder).
You can find these two bots in package :code:`tests.behavior_tests.bots` .
These two bots will be instantiated as pytext fixture in :code:`tests.behavior_tests.fixture`, and be used in various behavior tests.

Relevant behavior tests should be collected inside the same module, following the naming convention *test_behaviorset*. For example, we have :code:`tests.behavior_tests.test_conversation` to test general bot conversation.
The conversation was made by default :code:`mmpy_bot.plugins` .

Each behavior test might look like this:

.. code-block:: python

	from tests.behavior_tests.fixture import driver

	def test_bot_respond_to_simple_message(driver):
	    driver.send_direct_message('hello')
	    driver.wait_for_bot_direct_message('hello sender!')

This is a simple hello test. 
The driver is imported from fixture, and send into test function.
In the test, firstly the driver sends a direct message 'hello', and waits for response 'hello sender!'.
If the response does not show up in 10 seconds (default), an *AssertionError* will be raised.

For more message sending methods and options, please checkout :code:`tests.behavior_tests.bots.driver.py`. 


Run behavior tests
------------------

To perform behavior tests, some settings are necessary for bots to login to mattermost server for test.

1. Set up a mattermost server for test
2. Create two user accounts for bots, e.g. 'driverbot' and 'testbot'
3. Create a team, e.g. 'test-team', and add 'driverbot' and 'testbot' into the team
4. Make sure the default public channel 'off-topic' exists
5. Create a private channel, e.g. 'test', in team 'test-team', and add 'driverbot' and 'testbot' into the private channel

Optionally, if you like to test webhooks and other behaviors which requires admin privilege, please also assign 'drivebot' ADMIN privilege on your testing server, and set 

.. code-block:: python

	config.pytest_config.DRIVER_ADMIN_PRIVILEGE = True

If :code:`DRIVER_ADMIN_PRIVILEGE` is not set True, relevant tests will be skipped.

Set these environment variables (replace set command depending on your OS):

.. code-block:: bash

	$ set BOT_URL = 'http://SERVER_HOST_DN/api/v4'
	$ set DRIVERBOT_LOGIN = 'driverbot@mail'
	$ set DRIVERBOT_NAME = 'driverbot'
	$ set DRIVERBOT_PASSWORD = 'driverbot_password'
	$ set TESTBOT_LOGIN = 'testbot@mail'
	$ set TESTBOT_NAME = 'testbot_name'
	$ set TESTBOT_PASSWORD = 'testbot_password'
	$ set BOT_TEAM = 'test-team'
	$ set BOT_CHANNEL = 'off-topic'
	$ set BOT_PRIVATE_CHANNEL = 'test'

Then you should be ready to run behavior tests:

.. code-block:: bash

	$ pytest tests\behavior_tests


Run all the tests:
------------------

Set environment variables needed for behavior tests as mentioned above.

.. code-block:: bash

	$ pytest


Test coverage:
--------------

Install pytest-cov_:

.. _pytest-cov: https://pypi.org/project/pytest-cov/

.. code-block:: bash

	$ pip install pytest-cov

Set necessary configuration as described above, and run:

.. code-block:: bash

	$ py.test --cov=mmpy_bot tests\

It automatically runs tests and measures code coverage of modules under mmpy_bot root dir.
Using "--cov-report" parameter to write report into "cov_html" folder by html format.

.. code-block:: bash

	py.test --cov-report html:logs\cov_html --cov=mmpy_bot tests\