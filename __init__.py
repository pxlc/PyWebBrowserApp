
import os

os.environ['PYWEBBROWSERAPP_ROOT'] = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

from .pwba.PyWebBrowserApp import PyWebBrowserAppBase
from .pwba.PyWebBrowserApp import register_op


