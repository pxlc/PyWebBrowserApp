
class PluginBase(object):

    def __init__(self):

        pass

    def _connect_to_app(self, plugin_name, app_send_to_webbrowser, debug, info, warning, error, critical):

        self.plugin_name = plugin_name

        self.app_functions = {
           'debug': debug,
           'info': info,
           'warning': warning,
           'error': error,
           'critical': critical,
           'send_to_webbrowser': app_send_to_webbrowser,
        }

    def debug(self, msg):
        self.app_functions['debug'](msg)

    def info(self, msg):
        self.app_functions['info'](msg)

    def warning(self, msg):
        self.app_functions['warning'](msg)

    def error(self, msg):
        self.app_functions['error'](msg)

    def critical(self, msg):
        self.app_functions['critical'](msg)

    def plugin_to_webbrowser(self, plugin_js_function_name, op_data):

        plugin_op = 'Plugin|%s|%s' % (self.plugin_name, plugin_js_function_name)
        self.app_functions['send_to_webbrowser'](plugin_op, op_data)

