
import os

os.environ['PYWEBBROWSERAPP_ROOT'] = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

from .pwba.PyWebBrowserAppBase import PyWebBrowserAppBase
from .pwba.PyWebBrowserAppBase import register_op

from .pwba.PyWebBrowserAppWithPluginsBase import PyWebBrowserAppWithPluginsBase

