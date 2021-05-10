
import threading
import traceback

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

    def setup_task(self, task_name, validation_to_start_fn, task_execution_fn):

        self.task_name = task_name

        # param signatures for task functions are:
        #
        #   validation_to_start_fn(task_data_d, ui_message_fn, LogLevels)
        #          |
        #          + -> returns bool, True if OK to start Task
        #
        #   task_execution_fn(task_data_d, ui_message_fn, ui_progress_fn, ui_task_ended_fn,
        #                     LogLevels, TaskStatuses)
        #
        self.validation_to_start_fn = validation_to_start_fn
        self.task_execution_fn = task_execution_fn

    # parm signature for the ui functions are:
    # 
    #   ui_message_fn(message, message_level)
    #
    #   ui_update_progress_fn(percent_complete)
    #
    #   ui_task_ended_fn(completion_status, completion_message)
    #
    def ui_message_fn(self, message, message_level):

        self.plugin_to_webbrowser('ui_message', {'message': message, 'message_level': message_level})

    def ui_update_progress_fn(self, percent_complete):

        self.plugin_to_webbrowser('ui_update_progress', {'percent_complete': percent_complete})

    def ui_task_ended_fn(self, completion_status, completion_message):

        self.plugin_to_webbrowser('ui_task_ended', {'completion_status': completion_status,
                                                    'completion_message': completion_message})

    def _task_execution_wrapper(self, task_data_d, ui_message_fn, ui_progress_fn, ui_task_ended_fn,
                                LogLevels, TaskStatuses):

        try:
            self.status = self.task_execution_fn(task_data_d, ui_message_fn, ui_progress_fn, ui_task_ended_fn,
                                                 LogLevels, TaskStatuses)
        except:
            self.status = TaskStatuses.ERRORED

            stack_trace = traceback.format_exc()
            msg = 'Exception occurred in Task execution function - stack trace follows.\n\n%s' % stack_trace
            self.ui_message_fn(msg, LogLevels.ERROR)

    def check_status(self):

        return self.status

    @register_plugin_op
    def start_task(self, task_data_d):

        if self.status in (TaskStatuses.WORKING, TaskStatuses.PAUSED):
            msg = 'Task is already running or is paused.'
            print(msg)
            print('')
            self.ui_message_fn(msg, LogLevels.WARNING)
            return

        try:
            is_valid_to_start = self.validation_to_start_fn(task_data_d, self.ui_message_fn, LogLevels)
        except:
            stack_trace = traceback.format_exc()
            msg = 'Exception occurred in Task validation function - stack trace follows.\n\n%s' % stack_trace
            self.ui_message_fn(msg, LogLevels.ERROR)
            return

        if not is_valid_to_start:
            msg = 'Task validation for start has FAILED.'
            self.ui_message_fn(msg, LogLevels.ERROR)
            return

        self.plugin_to_webbrowser('ui_disable_controls', {})

        try:
            self.execution_thread = threading.Thread(target=self._task_execution_wrapper,
                                                     args=(task_data_d,
                                                           self.ui_message_fn,
                                                           self.ui_update_progress_fn,
                                                           self.ui_task_ended_fn,
                                                           LogLevels,
                                                           TaskStatuses))
            self.status = TaskStatuses.WORKING
            self.execution_thread.start()
        except:
            stack_trace = traceback.format_exc()
            msg = 'Exception occurred starting Task thread - stack trace follows.\n\n%s' % stack_trace
            self.ui_message_fn(msg, LogLevels.ERROR)

            self.plugin_to_webbrowser('ui_enable_controls', {})
            return


