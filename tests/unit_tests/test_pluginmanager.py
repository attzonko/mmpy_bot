import sys

# Handle backwards compatibility with 2.7
try:
    from importlib import reload
except ImportError:
    pass

from mmpy_bot.bot import PluginsManager


def test__load_plugins():
    reload(sys)
    PluginsManager._load_plugins('tests.unit_tests.single_plugin')
    if 'tests.unit_tests.single_plugin' not in sys.modules:
        raise AssertionError()
    if 'tests.unit_tests.single_plugin.mock_plugin' not in sys.modules:
        raise AssertionError()


def test_init_plugins_default_plugins():
    reload(sys)
    PluginsManager().init_plugins()
    if 'mmpy_bot.plugins' not in sys.modules:
        raise AssertionError()


def test_init_plugins_specified_plugins():
    reload(sys)
    PluginsManager(plugins=['tests.unit_tests.local_plugins']).init_plugins()
    if 'tests.unit_tests.local_plugins' not in sys.modules:
        raise AssertionError()
    if 'tests.unit_tests.local_plugins.hello' not in sys.modules:
        raise AssertionError()
    if 'tests.unit_tests.local_plugins.busy' not in sys.modules:
        raise AssertionError()


def test_get_plugins():
    reload(sys)
    manager = PluginsManager(plugins=[
        'tests.unit_tests.single_plugin',
        'tests.unit_tests.local_plugins'])
    manager.init_plugins()
    matched_func_names = set()
    # test: has_matching_plugin, there should be two handlers for `hello`
    for func, args in manager.get_plugins('listen_to', 'hello'):
        if func:
            matched_func_names.add(func.__name__)
    if 'hello_send' not in matched_func_names or \
       'hello_send_alternative' not in matched_func_names:
        raise AssertionError(
            'hello_send and hello_send_alternative should both be loaded')
    # test: not has_matching_plugin (there is no handler for `hallo`)
    reload(sys)
    matched_func_names = set()
    for func, args in manager.get_plugins('listen_to', 'hallo'):
        if func:
            matched_func_names.add(func.__name__)
    if 'hello_send' in matched_func_names:
        raise AssertionError()
