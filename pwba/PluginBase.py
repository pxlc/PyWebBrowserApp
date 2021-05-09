
class PluginBase(object):

    def __init__(self):

        self.debug = None
        self.info = None
        self.warning = None
        self.error = None
        self.critical = None

    def _setup_logging_functions(self, debug, info, warning, error, critical):

        self.debug = debug
        self.info = info
        self.warning = warning
        self.error = error
        self.critical = critical

