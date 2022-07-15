import asyncio
import re
from unittest import mock

import click
import pytest

from mmpy_bot import ExamplePlugin, Settings, listen_to
from mmpy_bot.driver import Driver
from mmpy_bot.function import Function, MessageFunction, WebHookFunction, listen_webhook
from mmpy_bot.plugins import PluginManager
from mmpy_bot.webhook_server import NoResponse
from mmpy_bot.wrappers import WebHookEvent

from .event_handler_test import create_message


class TestFunction:
    def test_is_coroutine(self):
        async def coroutine(self, message):
            pass

        assert Function(coroutine, re.compile("")).is_coroutine

        def not_a_coroutine(self, message):
            pass

        assert not Function(not_a_coroutine, re.compile("")).is_coroutine

    def test_wrap_function(self):
        def wrapped():
            pass

        f = Function(wrapped, matcher=re.compile("a"))
        assert f.function is wrapped
        assert f.matcher.pattern == "a"

        # Verify that wrapping an already wrapped function also works
        new_f = Function(f, matcher=re.compile("b"))
        assert new_f.function is wrapped
        assert new_f.matcher.pattern == "b"
        assert f in new_f.siblings


def example_listener(self, message):
    # Used to copy the arg specs to mock.Mock functions.
    pass


class TestMessageFunction:
    def test_listen_to(self):
        pattern = "test_regexp"

        def original_function(self, message):
            pass

        wrapped_function = listen_to(pattern, re.IGNORECASE)(original_function)

        assert isinstance(wrapped_function, MessageFunction)
        # Verify that both the regexp and its flags are correct
        assert wrapped_function.matcher == re.compile(pattern, re.IGNORECASE)
        assert wrapped_function.function == original_function

    def test_arguments(self):
        # This function misses the `message` argument
        def function1(self, arg):
            pass

        with pytest.raises(TypeError):
            MessageFunction(function1, matcher=re.compile(""))

        # This function has the correct arguments, but not in the correct order
        def function2(self, arg, message):
            pass

        with pytest.raises(TypeError):
            MessageFunction(function2, matcher=re.compile(""))

        # This function should work just fine
        def function3(self, message):
            pass

        MessageFunction(function3, matcher=re.compile(""))

    def test_click_coroutine(self):
        with pytest.raises(
            ValueError,
            match="Combining click functions and coroutines is currently not supported",
        ):

            @listen_to("")
            @click.command()
            async def coroutine(self, message):
                pass

    def test_wrap_function(self):  # noqa
        def wrapped(self, message, arg1, arg2):
            return arg1, arg2

        f = MessageFunction(wrapped, matcher=re.compile(""))
        # Verify that the arguments are passed and returned correctly
        assert f(create_message(), "yes", "no") == ("yes", "no")

        # Verify that wrapping an already wrapped function also works
        new_f = MessageFunction(f, matcher=re.compile("a"))
        assert new_f.function is wrapped
        assert new_f.matcher.pattern == "a"
        assert f in new_f.siblings

    def test_click_function(self):
        @click.command()
        @click.option("--arg1", type=str, default="nothing")
        @click.option("--arg2", type=str, default="nothing either")
        @click.option("-f", "--flag", is_flag=True)
        def wrapped(self, message, arg1, arg2, flag):
            return arg1, arg2, flag

        f = MessageFunction(wrapped, matcher=re.compile(""))
        # Verify that the arguments are passed and returned correctly
        assert f(create_message(), "--arg1=yes --arg2=no") == ("yes", "no", False)
        assert f(create_message(), "-f --arg2=no") == ("nothing", "no", True)

        # If an incorrect argument is passed, the error and help string should be returned.
        def mocked_reply(message, response):
            assert "no such option: --nonexistent-arg" in response.lower()
            assert f.docstring in response

        f.plugin = ExamplePlugin()
        f.plugin.initialize(Driver(), PluginManager([f.plugin]), Settings())
        with mock.patch.object(
            f.plugin.driver, "reply_to", wraps=mocked_reply
        ) as mock_function:
            f(create_message(), "-f --arg2=no --nonexistent-arg")
            mock_function.assert_called_once()

    @mock.patch("mmpy_bot.driver.Driver.user_id", "qmw86q7qsjriura9jos75i4why")
    def test_needs_mention(self):  # noqa
        wrapped = mock.create_autospec(example_listener)
        wrapped.__qualname__ = "wrapped"
        f = listen_to("", needs_mention=True)(wrapped)
        f.plugin = ExamplePlugin()
        f.plugin.initialize(Driver(), PluginManager([f.plugin]), Settings())

        # The default message mentions the specified user ID, so should be called
        f(create_message(mentions=["qmw86q7qsjriura9jos75i4why"]))
        wrapped.assert_called_once()
        wrapped.reset_mock()

        # No mention, so the function should still only have been called once in total
        f(create_message(mentions=[]))
        wrapped.assert_not_called()

        # But if this is a direct message, we do want to trigger
        f(create_message(mentions=[], channel_type="D"))
        wrapped.assert_called_once()

    @mock.patch("mmpy_bot.driver.Driver.user_id", "qmw86q7qsjriura9jos75i4why")
    def test_direct_only(self):
        wrapped = mock.create_autospec(example_listener)
        wrapped.__qualname__ = "wrapped"
        f = listen_to("", direct_only=True)(wrapped)

        # A mention is not a direct message, so shouldn't trigger
        f(create_message(mentions=["qmw86q7qsjriura9jos75i4why"], channel_type="O"))
        wrapped.assert_not_called()

        f(create_message(mentions=[], channel_type="D"))
        wrapped.assert_called_once()

    def test_allowed_users(self):
        wrapped = mock.create_autospec(example_listener)
        wrapped.__qualname__ = "wrapped"
        # Create a driver with a mocked reply function
        driver = Driver()

        def fake_reply(message, text):
            assert "you do not have permission" in text.lower()

        driver.reply_to = mock.Mock(wraps=fake_reply)

        f = listen_to("", allowed_users=["Betty"])(wrapped)
        f.plugin = ExamplePlugin()
        f.plugin.initialize(driver, PluginManager([f.plugin]), Settings())

        # This is fine, the names are not caps sensitive
        f(create_message(sender_name="betty"))
        wrapped.assert_called_once()
        wrapped.reset_mock()

        # This is not fine, and we expect the fake reply to be called.
        f(create_message(sender_name="not_betty"))
        wrapped.assert_not_called()
        driver.reply_to.assert_called_once()


def example_webhook_listener(self, event):
    # Used to copy the arg specs to mock.Mock functions.
    pass


def create_webhook_event():
    return WebHookEvent(body={}, request_id="some_id", webhook_id="some_id")


class TestWebHookFunction:
    def test_listen_webhook(self):
        pattern = "test_regexp"
        wrapped_function = listen_webhook(pattern)(example_webhook_listener)
        assert isinstance(wrapped_function, WebHookFunction)
        # Verify that the regexp is correct
        assert wrapped_function.matcher == re.compile(pattern)
        assert wrapped_function.function == example_webhook_listener

    def test_arguments(self):
        # This function misses the `event` argument
        def function1(self, arg):
            pass

        with pytest.raises(TypeError):
            WebHookFunction(function1, matcher=re.compile(""))

        # This function has the correct arguments, but not in the correct order
        def function2(self, arg, event):
            pass

        with pytest.raises(TypeError):
            WebHookFunction(function2, matcher=re.compile(""))

        # This function should work just fine
        def function3(self, event):
            pass

        WebHookFunction(function3, matcher=re.compile(""))

    def test_click_exception(self):
        with pytest.raises(
            TypeError,
            match="Webhook functions can't be click commands",
        ):
            listen_webhook("")(click.command()(example_webhook_listener))

    def test_ensure_response(self):
        p = ExamplePlugin()
        plugin_manager = PluginManager([p])
        p.initialize(Driver(), plugin_manager, Settings())

        def mock_respond(event, response):
            event.responded = True

        # SCENARIO 1: We wrap a function that does not send a web response
        with mock.patch.object(
            p.driver, "respond_to_web", wraps=mock_respond
        ) as mocked:
            f = WebHookFunction(example_webhook_listener, matcher=re.compile(""))
            f.plugin = p
            event = create_webhook_event()

            f(event)
            # We expect the WebHookFunction to automatically respond NoResponse
            mocked.assert_called_once_with(event, NoResponse)
            assert event.responded

        # SCECNARIO 2: Same scenario as above, but with asyncio
        async def webhook_function(self, event):
            pass

        with mock.patch.object(
            p.driver, "respond_to_web", wraps=mock_respond
        ) as mocked:
            f = WebHookFunction(webhook_function, matcher=re.compile(""))
            f.plugin = p
            event = create_webhook_event()

            # Asyncio helper to emulate running from async function
            async def run():
                await f(event)

            asyncio.run(run())
            # We expect the WebHookFunction to automatically respond NoResponse
            mocked.assert_called_once_with(event, NoResponse)
            assert event.responded

        # SCENARIO 3: We wrap a function that does send a web response
        def webhook_function(self, event):
            self.driver.respond_to_web(event, "Hello!")

        with mock.patch.object(
            p.driver, "respond_to_web", wraps=mock_respond
        ) as mocked:
            f = WebHookFunction(webhook_function, matcher=re.compile(""))
            f.plugin = p
            event = create_webhook_event()

            f(event)
            # We expect the WebHookFunction to not respond anything, since the function
            # itself already responded 'Hello!'.
            mocked.assert_called_once_with(event, "Hello!")
            assert event.responded

        # SCNEARIO 4: Same scenario as above, but with asyncio
        async def webhook_function(self, event):
            self.driver.respond_to_web(event, "Hello!")

        with mock.patch.object(
            p.driver, "respond_to_web", wraps=mock_respond
        ) as mocked:
            f = WebHookFunction(webhook_function, matcher=re.compile(""))
            f.plugin = p
            event = create_webhook_event()

            # Asyncio helper to emulate running from async function
            async def run():
                await f(event)

            asyncio.run(run())
            # We expect the WebHookFunction to not respond anything, since the function
            # itself already responded 'Hello!'.
            mocked.assert_called_once_with(event, "Hello!")
            assert event.responded
