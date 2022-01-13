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
import getpass
import logging
import datetime
import traceback
import subprocess

try:
    from PyWebBrowserApp import PyWebBrowserAppBase, register_op
except:
    # if import fails try import from package name that is all lowercase
    from pywebbrowserapp import PyWebBrowserAppBase, register_op

try:
    unicode
except:
    unicode = str

LAUNCHER_APP_ROOT = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
os.environ['LAUNCHER_APP_ROOT'] = LAUNCHER_APP_ROOT

_BASE_SYS_PATH = sys.path[:]
_BASE_OS_ENVIRON = dict(os.environ.copy())


class CustomPyWebBrowserApp(PyWebBrowserAppBase):

    BTN_HTML_TEMPLATE = '''
<button class="btn btn-secondary tool_img_btn" onclick="launch_app('{APP}');" style="padding: 4px;"
        title="{LABEL}">
    <img class="tool_img highlight" src="file://{ICON_PATH}" />
</button>'''

    def __init__(self, app_module_path, width=600, height=240,
                 start_html_filename='', template_dirpath='', config_filepath='',
                 log_to_shell=False, log_level_str='', webbrowser_path='', on_start_options_d=None)

        super(CustomPyWebBrowserApp, self).__init__(app_module_path, width=width, height=height,
                                                    template_dirpath=template_dirpath,
                                                    start_html_filename=start_html_filename,
                                                    config_filepath=config_filepath,
                                                    log_to_shell=log_to_shell,
                                                    log_level_str=log_level_str,
                                                    webbrowser_path=webbrowser_path,
                                                    on_start_options_d=on_start_options_d)

        # Do any required data set-up for your app here
        self.launcher_config_d = {}

    # --------------------------------------------------------------------------------------------------------
    # "setup_extra_template_vars()" is a REQUIRED override method
    #
    #  Establish any values for template vars in this method that you need to use in your HTML template file.
    # --------------------------------------------------------------------------------------------------------
    def setup_extra_template_vars(self):

        if sys.platform == 'win32':
            user_app_temp_root = os.path.join(os.getenv('TEMP'),
                                              'PYWEBBROWSERAPP_LAUNCHER_APP').replace('\\', '/')
        else:
            user_app_temp_root = os.path.join(os.getenv('HOME'),
                                              '.PYWEBBROWSERAPP_LAUNCHER_APP').replace('\\', '/')

        app_window_title = 'My Custom Launcher'

        if not os.path.exists(user_app_temp_root):
            os.makedirs(user_app_temp_root)

        user = getpass.getuser()

        extra_vars = {
            'LAUNCHER_APP_ROOT': LAUNCHER_APP_ROOT,
            'LOG_FILES_ROOT': user_app_temp_root,
            'USER_LOGIN': user,
            'WINDOW_TITLE': app_window_title,
        }
        return extra_vars

    # --------------------------------------------------------------------------------------------------------
    #  Register any callback op handler methods in this way ...
    #
    #      @register_op
    #      def my_op_handler(self, op_data):
    #          # op_data is data dict received from JavaScript side
    #          for op_data_key in sorted(op_data.keys()):
    #              self.info('    %s = %s' % (op_data_key, op_data[op_data_key]))
    #
    #    NOTE: DO NOT register an op handler method named "print_message" (that is a default one
    #          provided by the base class)
    # --------------------------------------------------------------------------------------------------------

    def _get_btn_info_exe_path(self, app_button_info):

        exe_path_value = app_button_info['exe_path'].get(sys.platform, None)

        if type(exe_path_value) is list:
            for exe_path in exe_path_value:
                if os.path.isfile(exe_path):
                    return exe_path
            return None

        elif type(exe_path_value) in (str, unicode):
            if '/' not in exe_path_value:
                # this is just a command that should run on command line of OS
                return exe_path_value
            # otherwise if it is a full path then test to see if it exists
            return exe_path_value if os.path.isfile(exe_path_value) else None

        else:
            return None

    @register_op
    def build_app_buttons(self, op_data):

        try:
            show_code = op_data.get('show_code', '')

            launcher_config_file = '%s/launcher_config.json' % LAUNCHER_APP_ROOT

            with open(launcher_config_file, 'r') as fp:
                self.launcher_config_d = json.load(fp)

            for app_button_info in self.launcher_config_d.get('app_buttons', []):

                exe_path = self._get_btn_info_exe_path(app_button_info)
                if not exe_path:
                    continue

                app_button_info['exe_path'] = exe_path
                icon_path = os.path.expandvars(app_button_info['icon_path'])
                btn_entry_html_str = self.BTN_HTML_TEMPLATE.format(
                                            LABEL=app_button_info['label'],
                                            ICON_PATH=icon_path,
                                            APP=app_button_info['app'])

                self.send_to_webbrowser('add_app_button', {'btn_entry_html': btn_entry_html_str})
        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')

    @register_op
    def launch_app(self, op_data):

        try:
            self.info('')
            self.info(':: op_data is %s' % op_data)
            self.info('')

            app = op_data['app_name']
            show_code = op_data['show_code']

            found_app_button_info = {}

            for app_button_info in self.launcher_config_d.get('app_buttons', []):
                if app == app_button_info['app']:
                    found_app_button_info.update(app_button_info)
                    break

            if not found_app_button_info:
                raise Exception('No app button info found for app "%s"' % app)

            # TODO: Set show environment here using your studio's environment system using show_code

            # Then run the application
            cmd_and_args = [ found_app_button_info['exe_path'] ]

            if 'exe_args' in found_app_button_info:
                exe_args = []
                exe_args_value = found_app_button_info['exe_args']
                if type(exe_args_value) is dict:
                    exe_args = exe_args_value.get(sys.platform, None)
                    if type(exe_args) is None:
                        raise Exception('No arguments specified for platform "%s"' % sys.platform)
                elif type(exe_args_value) is list:
                    exe_args = exe_args_value
                else:
                    raise Exception('Only expecting either dict or list for "exe_args" key value.')

                cmd_and_args += [ os.path.expandvars(arg) for arg in exe_args ]

            cflags = 0
            if sys.platform == 'win32':
                # be sure to open subprocess in a new process group so closing launcher doesn't kill
                # subprocess
                cflags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                # not sure if anything is needed on linux side to fork subprocess but do it here if so
                pass

            p = subprocess.Popen(cmd_and_args, creationflags=cflags)

            # Reset environment back to vanilla settings
            sys.path = _BASE_SYS_PATH[:]
            os.environ.clear()
            os.environ.update(_BASE_OS_ENVIRON)

        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')


