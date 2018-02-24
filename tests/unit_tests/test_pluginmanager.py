import sys, logging
import pytest
from mattermost_bot.bot import PluginsManager

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_load_single_plugin():
    assert 'single_plugin' not in sys.modules
    PluginsManager()._load_plugins('single_plugin')
    assert 'single_plugin' in sys.modules
    assert 'single_plugin.mock_plugin' in sys.modules

def test_load_init_plugins():
	PluginsManager().init_plugins()
	assert 'mattermost_bot.plugins' in sys.modules

def test_load_local_plugins():
	assert 'local_plugins' not in sys.modules
	PluginsManager(plugins=['local_plugins']).init_plugins()
	assert 'local_plugins' in sys.modules
	assert 'local_plugins.hello' in sys.modules
	assert 'local_plugins.busy' in sys.modules

def test_get_plugins():
	manager = PluginsManager(plugins=['single_plugin', 'local_plugins'])
	manager.init_plugins()
	matched_func_names = set()
	# test: has_matching_plugin
	for func, args in manager.get_plugins('listen_to', 'hello'):
		if func:
			matched_func_names.add(func.__name__)
	assert 'hello_send' in matched_func_names
	assert 'hello_send_alternative' in matched_func_names
	# test: not has_matching_plugin
	matched_func_names = set()
	for func, args in manager.get_plugins('listen_to', 'hallo'):
		if func:
			matched_func_names.add(func.__name__)
	assert 'hello_send' not in matched_func_names
	assert 'hello_send_alternative' not in matched_func_names
