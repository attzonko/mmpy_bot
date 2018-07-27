import logging
from mmpy_bot.dispatcher import MessageDispatcher
from mmpy_bot import settings

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_messagedispatcher__ignore_sender():
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
