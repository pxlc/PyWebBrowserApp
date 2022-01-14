
import os
import sys
import traceback

from PyWebBrowserApp import PluginBase
from PyWebBrowserApp import register_plugin_op


class Plugin(PluginBase):

    def __init__(self):

        super(Plugin, self).__init__()
        self.name = '${P}'
        self.user_profile_path = os.getenv('USERPROFILE').replace('\\', '/') \
                                    if sys.platform == 'win32' else ''

    @register_plugin_op
    def validate_dirpath(self, op_data):

        try:
            callback_fn_name = op_data.get('callback_fn_name', '')
            dirpath_to_validate = os.path.expandvars(op_data.get('dirpath_to_validate', '')).replace('\\', '/')

            if not dirpath_to_validate:
                self.plugin_to_webbrowser('response_to_validate_dirpath',
                                        {'is_path_valid': False, 'callback_fn_name': callback_fn_name,
                                            'dirpath_value': '', 'dir_items_info': dir_items_info})
            is_path_valid = False
            dir_items_info = None

            if len(dirpath_to_validate) == 2 and dirpath_to_validate[1] == ':':
                dirpath_to_validate += '/'

            if os.path.isdir(dirpath_to_validate):
                is_path_valid = True
                dir_items_info = {'files': [], 'folders': []}

                do_not_include_list = []
                if sys.platform == 'win32' and \
                        dirpath_to_validate.lower() == self.user_profile_path.lower():
                    do_not_include_list = ['My Documents', 'Application Data', 'Cookies', 'Local Settings',
                                            'NetHood', 'PrintHood', 'Recent', 'SendTo', 'Start Menu',
                                            'Templates']

                items = [f for f in sorted(os.listdir(dirpath_to_validate)) if f not in do_not_include_list]

                for i in items:
                    i_path = '%s/%s' % (dirpath_to_validate, i)
                    if os.path.isdir(i_path):
                        dir_items_info['folders'].append(i)
                    else:
                        # otherwise assume it is a file
                        dir_items_info['files'].append(i)

            self.plugin_to_webbrowser('response_to_validate_dirpath',
                                      {'is_path_valid': is_path_valid, 'callback_fn_name': callback_fn_name,
                                       'dirpath_value': dirpath_to_validate, 'dir_items_info': dir_items_info})
        except:
            err_msg = '[in plugin ${P}.validate_dirpath() method] Exception raised ...\n%s' % traceback.format_exc()
            self.error(err_msg)
            self.plugin_to_webbrowser('response_to_validate_dirpath',
                                      {'is_path_valid': 'error', 'callback_fn_name': callback_fn_name,
                                       'dirpath_value': dirpath_to_validate, 'dir_items_info': None,
                                       'error_message': err_msg})

    @register_plugin_op
    def test_plugin_callback(self, op_data):

        # self.info(op_data.get('message', ''))
        print('Hello from ${P} callback')

    @register_plugin_op
    def roundtrip_from_js(self, op_data):

        alert_msg = op_data.get('alert_msg', '???')
        self.info('[Plugin "%s"] in roundtrip_from_js() method, got alert_msg "%s"' % (self.name, alert_msg))

        self.plugin_to_webbrowser('roundtrip_from_python', {'alert_msg': alert_msg})

    # -------------------------------------------------------------------------
    # NOTE: to get list of drive letters for quick links use Windows command:
    #
    #            wmic logicaldisk get name
    #
    #       ... get output from running command as a subprocess. First line is
    #       a header line (so skip it); after that will be a list of active
    #       drive letters, one per line.
    # -------------------------------------------------------------------------

