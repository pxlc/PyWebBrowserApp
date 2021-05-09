
from PyWebBrowserApp import PluginBase
from PyWebBrowserApp import register_plugin_op


class PluginSubclass(PluginBase):

    def __init__(self):

        super(PluginSubclass, self).__init__()


    @register_plugin_op
    def test_plugin_callback(self, op_data):

        # self.info(op_data.get('message', ''))
        print('Hello from ${P} callback')

