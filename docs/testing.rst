.. _testing:


Testing
=======

mmpy_bot develops all tests based on pytest. If you need to add your own tests and run tests, please install the dev requirements.

.. code-block:: bash

	$ pip install -r dev-requirements.txt

All the tests are put in `mmpy_bot\tests`.
There are two test packages: :code:`unit_tests` and :code:`integration_tests`.

Tests which can be performed by a single bot without requiring a server or interaction with other bots should be kept in the :code:`unit_tests` package.
Tests that require interactions between bots on a mattermost server belong to the :code:`integration_tests` package.


Adding unit tests
--------------

There are multiple test modules inside unit_tests package, one for each module in the code.
The naming convention of these modules is *modulename_test*.
Inside each module, there will be several test functions with naming convention *test_methodname*, grouped into classes for each corresponding class in the code.
If you need to add more unit tests, please consider following these conventions.


Running the unit tests
--------------

To run the unit tests (in parallel), simply execute:

.. code-block:: bash

	$ pytest -n auto tests\unit_tests


Addding integration tests
------------------

The integration tests are run on the `jneeven:mattermost-bot-test` docker image, for which dockerfiles are provided in the `tests/intergration_tests` folder.
The tests are defined as interactions between a bot (the responder) and a driver (the one sending test messages), which live inside the docker image.
Their respective tokens are available in `tests/integration_tests/utils.py`, and the two bots are available as pytest fixtures so they can be easily re-used.
Note that while the bot is also a fixture, it should not be used in any functions.
It will simply be started whenever the integration tests are executed.

An integration test might look like this (also have a look at the actual code in `tests/integration_tests/test_example_plugin.py`):

.. code-block:: python

	from tests.integration_tests.utils import start_bot  # noqa, only imported so that the bot is started
	from tests.integration_tests.utils import MAIN_BOT_ID, OFF_TOPIC_ID, RESPONSE_TIMEOUT, TEAM_ID
	from tests.integration_tests.utils import driver as driver_fixture
	from tests.integration_tests.utils import expect_reply

	# Hacky workaround to import the fixture without linting errors
	driver = driver_fixture

	# Verifies that the bot is running and listening to this non-targeted message
	def test_start(driver):
		post = driver.create_post(OFF_TOPIC_ID, "starting integration tests!")
		# Checks whether the bot has sent us the expected reply
		assert expect_reply(driver, post)["message"] == "Bring it on!"

In this test, the driver sends a message in the "off-topic" channel, and waits for the bot to reply 'Bring it on!'.
If no reply occurs within a default response timeout (15 seconds by default, but this can be passed as an argument to `expect_reply`), an exception will be raised.
The driver fixture is imported from the utils and can be re-used in every test function simply by adding it as a function argument.



Running the integration_tests
------------------

Running the integration_tests is easy: simply `cd` into `tests/integration_tests`, and run `docker-compose up -d` to start a local mattermost server.
Then run `pytest -n auto .` to start the tests! For more info about the integration tests an the docker server, have a look at `tests/integration_tests/README.md`.

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
