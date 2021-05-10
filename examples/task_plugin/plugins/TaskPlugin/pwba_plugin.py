
from PyWebBrowserApp import PluginBase
from PyWebBrowserApp import register_plugin_op

# + ============================================================================
# |
# |    TaskPlugin plugin Python class
# |
# + ============================================================================

class TaskStatuses(object):

    NOT_STARTED = 'not_started'
    WORKING = 'working'
    COMPLETED = 'completed'
    ERRORED = 'errored'
    PAUSED = 'paused'


class LogLevels(object):

    INFO = 'info'
    DEBUG = 'debug'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class Plugin(PluginBase):

    def __init__(self):

        super(Plugin, self).__init__()

        self.task_name = ''

        self.execution_thread = None

        self.validation_to_start_fn = None
        self.task_execution_fn = None
        self.execution_thread = None

        self.status = TaskStatuses.NOT_STARTED

        self.ui_message_fn = None
        self.ui_progress_fn = None
        self.ui_task_ended_fn = None

    def setup_task(self, task_name, validation_to_start_fn, task_execution_fn, ui_message_fn,
                    ui_progress_fn, ui_task_ended_fn):

        self.task_name = task_name

        # param signatures for task functions are:
        #
        #   validation_to_start_fn(task_data_d, ui_message_fn) -> returns bool, True if OK to start Task
        #
        #   task_execution_fn(task_data_d, ui_message_fn, ui_progress_fn, ui_task_ended_fn,
        #                     LogLevels, TaskStatuses)
        #
        self.validation_to_start_fn = validation_to_start_fn
        self.task_execution_fn = task_execution_fn

        # parm signature for the ui functions are:
        # 
        #   ui_message_fn(message, log_level)
        #
        #   ui_progress_fn(percent_complete)
        #
        #   ui_task_ended_fn(completion_status, completion_message)
        #
        self.__ui_message_fn = ui_message_fn
        self.ui_progress_fn = ui_progress_fn
        self.ui_task_ended_fn = ui_task_ended_fn

    def ui_message_fn(self, message, log_level):

        self.__ui_message_fn('[%s] %s' % (self.task_name, message), log_level)

    def check_status(self):

        return self.status

    @register_plugin_op
    def start_task(self, task_data_d):

        if self.status in (self.WORKING, self.PAUSED):
            self.ui_message_fn('Task is already running or is paused.', LogLevels.WARNING)
            return

        if self.validation_to_start_fn(task_data_d, self.ui_message_fn):
            self.ui_message_fn('Task validation for start has FAILED.', LogLevels.ERROR)
            return

        self.execution_thread = threading.Thread(target=self.task_execution_fn,
                                                 args=(task_data_d,
                                                       self.ui_message_fn,
                                                       self.ui_progress_fn,
                                                       self.ui_task_ended_fn,
                                                       LogLevels,
                                                       TaskStatuses))
        self.status = TaskStatuses.WORKING
        self.execution_thread.start()


