
import os
import sys

# -------------------------------------------------------------------------------------------------
#
#  Make sure third party packages are placed in the path
#
# -------------------------------------------------------------------------------------------------
__PKG_ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('//', '/')
__PYWEBSCKTSRVR_PATH = '%s/thirdparty/python-websocket-server' % __PKG_ROOT_PATH
sys.path.insert(0, __PYWEBSCKTSRVR_PATH)  # for python-websocket-server package
os.environ['PYTHONPATH'] = os.pathsep.join([__PYWEBSCKTSRVR_PATH, os.getenv('PYTHONPATH')]) \
                            if os.getenv('PYTHONPATH') else __PYWEBSCKTSRVR_PATH

# -------------------------------------------------------------------------------------------------
#
#  Set env var for the root of this package to make included resources available
#
# -------------------------------------------------------------------------------------------------
os.environ['PYWEBBROWSERAPP_ROOT'] = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

# -------------------------------------------------------------------------------------------------
#
#  Import modules to expose for this package
#
# -------------------------------------------------------------------------------------------------
from .pwba.PyWebBrowserAppBase import PyWebBrowserAppBase

from .pwba.op_registry import register_op
from .pwba.op_registry import register_plugin_op

from .pwba.PluginBase import PluginBase

from .pwba import launcher

from . import package_test


