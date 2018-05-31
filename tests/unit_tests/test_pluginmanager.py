import sys, logging
from importlib import reload
from mmpy_bot.bot import PluginsManager

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_load_single_plugin():
	reload(sys)
	PluginsManager()._load_plugins('single_plugin')
	if 'single_plugin' not in sys.modules:
		raise AssertionError()
	if 'single_plugin.mock_plugin' not in sys.modules:
		raise AssertionError()

def test_load_init_plugins():
	reload(sys)
	PluginsManager().init_plugins()
	if 'mmpy_bot.plugins' not in sys.modules:
		raise AssertionError()

def test_load_local_plugins():
	reload(sys)
	PluginsManager(plugins=['local_plugins']).init_plugins()
	if 'local_plugins' not in sys.modules:
		raise AssertionError()
	if 'local_plugins.hello' not in sys.modules:
		raise AssertionError()
	if 'local_plugins.busy' not in sys.modules:
		raise AssertionError()

def test_get_plugins():
	reload(sys)
	manager = PluginsManager(plugins=['single_plugin', 'local_plugins'])
	manager.init_plugins()
	matched_func_names = set()
	# test: has_matching_plugin
	for func, args in manager.get_plugins('listen_to', 'hello'):
		if func:
			matched_func_names.add(func.__name__)
	if 'hello_send' not in matched_func_names:
		raise AssertionError()
	if 'hello_send_alternative' not in matched_func_names:
		raise AssertionError()
	# test: not has_matching_plugin (there is no such plugin `hallo`)
	reload(sys)
	matched_func_names = set()
	for func, args in manager.get_plugins('listen_to', 'hallo'):
		if func:
			matched_func_names.add(func.__name__)
	if 'hello_send' in matched_func_names:
		raise AssertionError()
	if 'hello_send_alternative' in matched_func_names:
		raise AssertionError()
