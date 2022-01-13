# -------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2018-2021 pxlc@github
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------------------

import os
import sys
import json
import getopt
import logging
import importlib

__PKG_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('//', '/')
__PYWEBSCKTSRVR_PATH = '%s/thirdparty/python-websocket-server' % __PKG_ROOT_PATH
sys.path.insert(0, __PYWEBSCKTSRVR_PATH)  # for python-websocket-server package
os.environ['PYTHONPATH'] = os.pathsep.join([__PYWEBSCKTSRVR_PATH, os.getenv('PYTHONPATH')]) \
                            if os.getenv('PYTHONPATH') else __PYWEBSCKTSRVR_PATH

__PKG_IS_AVAILABLE = False
try:
    from PyWebBrowserApp import package_test
    __PKG_IS_AVAILABLE = True
except:
    __PKG_IS_AVAILABLE = False

if not __PKG_IS_AVAILABLE:
    # If the 'PyWebBrowserApp' package is unavailable to import from then it's not in the sys.path, so we
    # get the appropriate root path added to sys.path and PYTHONPATH for the import of the app module that
    # will in turn import from PyWebBrowserApp ...
    #
    __PKG_PARENT_PATH = os.path.dirname(
                            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('//', '/')
    sys.path.insert(0, __PKG_PARENT_PATH)
    os.environ['PYTHONPATH'] = os.pathsep.join([__PKG_PARENT_PATH, os.getenv('PYTHONPATH')]) \
                                if os.getenv('PYTHONPATH') else __PKG_PARENT_PATH

from PyWebBrowserApp import launcher


def usage():

    script = os.path.basename(os.path.abspath(__file__))

    print('')
    print('  Usage: python {} [OPTIONS] <app_module_path>'.format(script))
    print('')
    print('     -h | --help ... print this usage message')
    print('     -s | --shell-logging ... log messages to shell console as well')
    print('     -o <START_OPTIONS_JSON> | --options-on-start <START_OPTIONS_JSON> ... JSON string with on start options')
    print('     -l <LOGLEVEL> | --log-level <LOGLEVEL> ... "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"')
    print('     -b <WEBBROWSERPATH> | --browser-path <WEBBROWSERPATH> ... full path to webbrowser executable')
    print('     -c <CONFIGFILE> | --config-file <CONFIGFILE> ... full path to config file to use')
    print('     -t <TEMPLATEFILEPATH> | --template-filepath <TEMPLATEFILEPATH>')
    print('                                                    ... full path to HTML template to launch app with.')
    print('     -W <window_width> | --width <window_width> ... integer value of pixels width of window to open')
    print('     -H <window_height> | --height <window_height> ... integer value of pixels height of window to open')
    print('')


def main(in_args):

    short_opt_str = 'hso:l:b:c:t:W:H:'
    long_opt_list = ['help', 'shell-logging', 'options-on-start=', 'log-level=', 'browser-path=', 'config-file=',
                     'template-filepath', 'width=', 'height=']
    try:
        opt_list, arg_list = getopt.getopt(in_args, short_opt_str, long_opt_list)
    except getopt.GetoptError as err:
        print('')
        print(str(err))
        usage()
        sys.exit(2)

    shell_logging = False
    on_start_options_d = None
    log_level_str = 'ERROR'
    webbrowser_path = ''
    config_filepath = ''
    template_filepath = ''
    width = 0
    height = 0

    for opt_flag, opt_value in opt_list:
        if opt_flag in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt_flag in ('-s', '--shell-logging'):
            shell_logging = True
        elif opt_flag in ('-o', '--options-on-start'):
            on_start_options_d = json.loads(opt_value)
            if on_start_options_d:
                print('')
                print('>>> On start options:')
                print('')
                print(json.dumps(on_start_options_d, indent=4, sort_keys=True))
                print('')
        elif opt_flag in ('-l', '--log-level'):
            log_level_str = opt_value
        elif opt_flag in ('-b', '--browser-path'):
            webbrowser_path = opt_value
        elif opt_flag in ('-c', '--config-file'):
            config_filepath = opt_value
        elif opt_flag in ('-t', '--template-filepath'):
            template_filepath = opt_value
        elif opt_flag in ('-W', '--width'):
            width = int(opt_value)
        elif opt_flag in ('-H', '--height'):
            height = int(opt_value)

    if len(arg_list) != 1:
        print('')
        print('*** ERROR: expecting 1 argument ...')
        usage()
        sys.exit(3)

    app_module_path = arg_list[0]

    launcher.launch_app(app_module_path, shell_logging=shell_logging, log_level_str=log_level_str,
                        config_filepath=config_filepath, template_filepath=template_filepath,
                        width=width, height=height, webbrowser_path=webbrowser_path,
                        on_start_options_d=on_start_options_d)


if __name__ == '__main__':

    main(sys.argv[1:])


