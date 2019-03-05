import os
import json
import pytest
try:
    from unittest import mock
except ImportError:
    from mock import mock
from mmpy_bot.dispatcher import Message


@pytest.fixture(scope="function")
def message():
    with open(os.sep.join(
              ['tests', 'unit_tests', 'test_data', 'message.json']),
              'r') as f:
        return Message(client=None, body=json.load(f), pool=None)


@pytest.fixture(scope="function")
def thread_message():
    with open(os.sep.join(
              ['tests', 'unit_tests', 'test_data', 'thread_message.json']),
              'r') as f:
        return Message(client=None, body=json.load(f), pool=None)


def test_get_team_id(message):
    if message.get_team_id() != "au64gza3iint3r31e7ewbrrasw":
        raise AssertionError()


def test_get_message(message):
    if message.get_message() != "hello":
        raise AssertionError()


def test_is_direct_message(message):
    if message.is_direct_message() is True:
        raise AssertionError()


def test_get_mentions(message):
    if 'qmw86q7qsjriura9jos75i4why' not in message.get_mentions():
        raise AssertionError()


def test_channel(message):
    if message.channel != '4fgt3n51f7ftpff91gk1iy1zow':
        raise AssertionError()


def test_body(message):
    with open(os.sep.join(
              ['tests', 'unit_tests', 'test_data', 'message.json']),
              'r') as f:
        body = json.load(f)
        if message.body != body:
            raise AssertionError()


@mock.patch("mmpy_bot.dispatcher.Message.send")
def test_first_reply_in_thread(mo_send, thread_message):
    thread_message.reply_thread("third message in thread")
    mo_send.assert_called_once_with(
        "@betty: third message in thread",
        files=None,
        props={},
        pid='wqpuawcw3iym3pq63s5xi1776r'
    )
