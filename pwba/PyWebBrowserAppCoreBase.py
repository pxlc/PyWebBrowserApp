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
import ctypes
import getpass
import subprocess
import traceback
import logging

import jinja2

from websocket_server import WebsocketServer

# local imports
from . import util
from .op_registry import register_op
from .get_js import get_js_file_url
from .config import load_config_file
from .util import get_next_port_num

PYWEBBROWSERAPP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')
print('')
print('[PYWEBBROWSERAPP_ROOT]: %s' % PYWEBBROWSERAPP_ROOT)
print('')


class PyWebBrowserAppCoreBase(object):

    JS_FILE_URL = '%s/js/py_webbrowser_app.js' % PYWEBBROWSERAPP_ROOT
    PYWEBBROWSERAPP_ROOT = PYWEBBROWSERAPP_ROOT

    def __init__(self, app_module_filepath, webbrowser_path='', width=480, height=600, template_dirpath='',
                 start_html_filename='', config_filepath='', log_to_shell=False, log_level_str='',
                 app_temp_root='', webbrowser_data_path=''):

        self.webbrowser_path = webbrowser_path if webbrowser_path else self._get_webbrowser_exe_path()

        self.browser_name_tag = ''
        self.webbrowser_data_path = ''

        if not self.webbrowser_path:
            raise Exception('Chromium browser not found in common locations ... unable to run.')
        elif not os.path.isfile(self.webbrowser_path):
            raise Exception('Cannot find "%s" Chromium browser on this computer ... unable to run.')

        self.browser_name_tag = os.path.basename(self.webbrowser_path).split('.')[0]

        self.app_module_filepath = app_module_filepath.replace('\\','/')
        self.app_dir_path = os.path.dirname(self.app_module_filepath)
        self.app_module_filename = os.path.basename(self.app_module_filepath)

        cap_words = [ w.capitalize() for w in
                            self.app_module_filename.replace('_app.py','').replace('.py','').split('_') ]

        self.app_short_name = ''.join(cap_words)
        self.app_title_label = ' '.join(cap_words)  # default App Title

        self.app_temp_root = app_temp_root if app_temp_root else util.get_app_user_temp_path(self.app_short_name)
        if webbrowser_data_path:
            self.webbrowser_data_path = '%s_%s' % (webbrowser_data_path, self.browser_name_tag)
        else:
            self.webbrowser_data_path = os.path.join(self.app_temp_root, '%s_browser_%s' % (self.app_short_name,
                                                                                        self.browser_name_tag))
        self.config = load_config_file(config_filepath)

        self.user = getpass.getuser()

        tmpl_dir_path = template_dirpath if template_dirpath else self.app_dir_path
        self.j2_template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(tmpl_dir_path))

        self.port = get_next_port_num(self.config)

        self.session_start_dt_str = util.now_datetime_str('compact')
        self.session_id = '{a}_{u}_{dt}'.format(a=self.app_short_name, u=self.user, dt=self.session_start_dt_str)

        # use session_id as logger name
        log_filename = util.get_app_session_log_filename(dt_str=self.session_start_dt_str)
        self.log_file = os.path.join(self.app_temp_root, '%s_logs' % self.app_short_name, log_filename)

        print('')
        print(':: log file path: %s' % self.log_file)
        print(':: webbrowser data path: %s' % self.webbrowser_data_path)
        print('')

        # make sure log directory exists
        log_dirpath = os.path.dirname(self.log_file)
        if not os.path.isdir(log_dirpath):
            os.makedirs(log_dirpath)

        log_level_map = {
            'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        log_level = logging.ERROR
        if log_level_str in log_level_map:
            log_level = log_level_map.get(log_level_str)

        self.logger = logging.getLogger('{a}{dt}'.format(a=self.app_short_name,
                                                         dt=self.session_start_dt_str.replace('_','')))
        self.logger.setLevel( log_level )
        util.setup_logger(self.logger, self.log_file, log_level, log_to_shell=log_to_shell)

        self.session_file_path_pre = self.log_file.replace('.log', '')
        self.session_temp_dir_path = os.path.dirname(self.log_file)

        if not os.path.isdir(self.session_temp_dir_path):
            os.makedirs(self.session_temp_dir_path)

        self.ws_server = WebsocketServer(self.port)

        self.ws_server.set_fn_new_client(self._ws_new_client)
        self.ws_server.set_fn_client_left(self._ws_client_left)
        self.ws_server.set_fn_message_received(self._ws_message_from_client)

        self.webbrowser_client = None

        self.session_data = {}
        self.op_handler_info = {} # {'op_name': {'cb_fn': fn}}
        self.default_op_handler_fn = None

        self.width = width
        self.height = height

        self.webbrowser_process = None

        self.start_html_fname = start_html_filename if start_html_filename else self.auto_template_filename()

        self._setup_op_handlers()

    def setup_extra_template_vars(self):

        raise Exception('method setup_extra_template_vars() MUST be overridden in sub-class.')

    def _setup_op_handlers(self):

        # set up callbacks here
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if 'bound method' in str(attr) and hasattr(attr, '_op_name'):
                op_name = attr._op_name.split('.')[1] if '.' in attr._op_name else attr._op_name
                print('    adding op: %s' % op_name)
                self.add_op_handler(op_name, attr)

    def _get_webbrowser_exe_path(self):

        webbrowser_paths_by_platform = {
            'win32': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            ],
            'linux': [
                '/usr/bin/chromium',
                '/usr/bin/microsoft-edge-dev',
            ],
            'linux2': [
                '/usr/bin/chromium',
                '/usr/bin/microsoft-edge-dev',
            ]
        }
        webbrowser_path_list = webbrowser_paths_by_platform.get(sys.platform, [])
        webbrowser_path = ''

        for c_path in webbrowser_path_list:
            if os.path.isfile(c_path):
                webbrowser_path = c_path
                break

        return webbrowser_path

    def auto_template_filename(self):

        return 'T_{0}.html'.format(self.app_module_filename.replace('_app.py','').replace('.py',''))

    def generate_html_file(self, template_filename, all_plugins_html=''):

        template = self.j2_template_env.get_template(template_filename)

        template_vars = {
            'PYWEBBROWSERAPP_JS_URL': self.get_js_file_url(),
            'PORT': str(self.get_port_num()),
            'SESSION_ID': self.get_session_id(),
            'WIN_TITLE': self.get_app_title(),
            'APP_DIR_PATH': self.get_app_dir_path().replace('\\', '/'),
        }
        template_vars.update(self.setup_extra_template_vars())

        html = template.render(template_vars)

        if all_plugins_html:
            html = html.replace('</body>', '%s\n\n</body>' % all_plugins_html)

        html_file_path = self.build_session_filepath('APP_START', '.html')
        with open(html_file_path, 'w') as html_fp:
            html_fp.write(html)

        return html_file_path

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def _ws_new_client(self, client, server):

        if not self.webbrowser_client:
            self.webbrowser_client = client
            msg_obj = {'op': 'connection_status', 'session_id': self.session_id, 'data': {'status': 'CONNECTED'}}
            self.ws_server.send_message(client, json.dumps(msg_obj))

    def clean_up(self):
        pass

    def _ws_client_left(self, client, server):

        if client == self.webbrowser_client:
            if self.webbrowser_process:
                self.webbrowser_process.kill()
            self.ws_server.shutdown()
            self.clean_up()

    def _ws_message_from_client(self, client, server, message):

        if client != self.webbrowser_client:
            return

        msg_data = {}
        try:
            msg_data = json.loads(message)
        except:
            self.error('>>> ERROR: Unable to read data message from web browser client:\n\n%s' %
                        traceback.format_exc())
            self.error('>>> Here is the message string: @%s@ (type is %s)' % (message, type(message)))
            return

        op = msg_data.get('op')
        session_id = msg_data.get('session_id')
        op_data = msg_data.get('data', {})

        if not op or not session_id or type(op_data) is not dict:
            self.error('in PyWebBrowserApp._ws_message_from_client() ... no op or no session_id or op_data is not' \
                        ' a dictionary.')
            return
        if session_id != self.session_id:
            self.error('in PyWebBrowserApp._ws_message_from_client() ... incoming session_id ("%s") is not the same' \
                        ' as this app\'s stored session_id ("%s")' % (session_id, self.session_id))
            return

        # make sure the op has been registered, send error message if not
        if op not in self.op_handler_info:
            self.error('>>> ERROR: No op handler registered for op "%s" ... unable to process op' % op)
            return

        # delegate operation and its data to handler function
        try:
            fn = self.op_handler_info.get(op, {}).get('cb_fn')
        except:
            self.error('>>> ERROR: Exception raised running "%s" op handler:\n\n%s' %
                        (op, traceback.format_exc()))
            return

        if fn:
            try:
                fn(op_data)
            except:
                self.error('>>> ERROR: Exception raised running "%s" op handler:\n\n%s' %
                            (op, traceback.format_exc()))
        else:
            self.error('>>> ERROR: No function found for registered op handler "%s" ... unable to process op' % op)

    def set_app_title(self, title):
        self.app_title_label = title

    def get_app_dir_path(self):
        return self.app_dir_path

    def get_app_short_name(self):
        return self.app_short_name

    def get_app_title(self):
        return self.app_title_label

    def get_port_num(self):
        return self.port

    def get_session_id(self):
        return self.session_id

    def get_log_filepath(self):
        return self.log_file

    def get_js_file_url(self):
        return self.JS_FILE_URL

    def build_session_filepath(self, file_suffix, file_ext):
        return '{pre}_{suf}{ext}'.format(pre=self.session_file_path_pre, suf=file_suffix, ext=file_ext)

    def add_op_handler(self, op, op_callback_fn):

        self.op_handler_info[op] = {'cb_fn': op_callback_fn}

    def set_default_op_handler(self, default_op_callback_fn):

        self.default_op_handler_fn = default_op_callback_fn

    def send_to_webbrowser(self, webbrowser_op, webbrowser_op_data):

        if not self.webbrowser_client:
            self.warning('No webbrowser_client to send to!')
            return

        msg_data_str = json.dumps({'op': webbrowser_op, 'session_id': self.session_id, 'data': webbrowser_op_data})
        self.ws_server.send_message(self.webbrowser_client, msg_data_str)

    def start_(self):

        try:
            webbrowser_exe_path = self.webbrowser_path

            webbrowser_data_dir = self.webbrowser_data_path if self.webbrowser_data_path \
                                    else os.path.join(self.config.get('user_temp_root', os.getenv('TEMP')),
                                                      '_webbrowser_app_user_data')

            if not os.path.isdir(webbrowser_data_dir):
                os.makedirs(webbrowser_data_dir)

            cmd_arr = [
                webbrowser_exe_path,
                '--allow-file-access-from-files',
                '--window-size={w},{h}'.format(w=self.width, h=self.height),
                '--user-data-dir={0}'.format(webbrowser_data_dir),
                '--app=file:///{0}'.format(self.generate_html_file(self.start_html_fname)),
            ]

            if sys.platform == 'win32':
                SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
                ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
                CREATE_NO_WINDOW = 0x08000000 # From Windows API
                subprocess_flags = CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                subprocess_flags = 0
                
            self.webbrowser_process = subprocess.Popen(cmd_arr, creationflags=subprocess_flags)
            self.ws_server.run_forever()
        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')

    def launch(self):

        self.start_()

    @register_op
    def PyWebBrowserApp_print_message(self, op_data):

        log_level = op_data.get('log_level', 'info')
        message = op_data.get('message', '<NO_MESSAGE_RECEIVED>')

        log_fn_by_level = {
            'info': self.info,
            'debug': self.debug,
            'warning': self.warning,
            'error': self.error,
            'critical': self.critical,
        }

        if log_level not in log_fn_by_level:
            self.warning('Unknown log level "%s" received ... message follows ...')
            self.warning(message)
            return

        log_fn_by_level[log_level](message)


