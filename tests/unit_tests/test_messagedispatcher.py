import os
import json
import pytest
from mmpy_bot.dispatcher import MessageDispatcher
from mmpy_bot import settings


@pytest.fixture(scope="function")
def message():
    with open(os.sep.join(
              ['tests', 'unit_tests', 'test_data', 'message.json']),
              'r') as f:
        return json.load(f)


def test_get_message(message):
    if MessageDispatcher.get_message(message) != "hello":
        raise AssertionError()


def test_ignore_sender():
    dispatcher = MessageDispatcher(None, None)
    event = {'event': 'posted', 'data': {'sender_name': 'betty'}}
    event2 = {'event': 'posted', 'data': {'sender_name': 'Carter'}}
    # test by lowercase  / uppercase settings
    # set as 'Betty'
    settings.IGNORE_USERS = []  # clean up
    settings.IGNORE_USERS.append('Betty')
    if dispatcher._ignore_sender(event) is not True:
        raise AssertionError()
    # set as 'CARTER'
    settings.IGNORE_USERS.append('CARTER')
    if dispatcher._ignore_sender(event2) is not True:
        raise AssertionError()
