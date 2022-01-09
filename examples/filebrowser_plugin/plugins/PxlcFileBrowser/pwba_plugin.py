
import os

from PyWebBrowserApp import PluginBase
from PyWebBrowserApp import register_plugin_op


class Plugin(PluginBase):

    def __init__(self):

        super(Plugin, self).__init__()
        self.name = '${P}'

    @register_plugin_op
    def validate_dirpath(self, op_data):

        callback_fn_name = op_data.get('callback_fn_name', '')
        dirpath_to_validate = op_data.get('dirpath_to_validate', '')
        is_path_valid = False

        if os.path.isdir(dirpath_to_validate):
            is_path_valid = True
        else:
            # Sym-links manifest as files in Python so see if we can listdir() on it
            try:
                os.listdir(dirpath_to_validate)
                is_path_valid = True
            except:
                pass # leave as not valid

        self.plugin_to_webbrowser('response_to_validate_dirpath',
                                  {'is_path_valid': is_path_valid, 'callback_fn_name': callback_fn_name})

    @register_plugin_op
    def test_plugin_callback(self, op_data):

        # self.info(op_data.get('message', ''))
        print('Hello from ${P} callback')

    @register_plugin_op
    def roundtrip_from_js(self, op_data):

        alert_msg = op_data.get('alert_msg', '???')
        self.info('[Plugin "%s"] in roundtrip_from_js() method, got alert_msg "%s"' % (self.name, alert_msg))

        self.plugin_to_webbrowser('roundtrip_from_python', {'alert_msg': alert_msg})

