
import copy
import logging
import threading


class TaskStatuses(object):

    NOT_STARTED = 'not_started'
    WORKING = 'working'
    COMPLETED = 'completed'
    ERRORED = 'errored'
    PAUSED = 'paused'


class TaskThread(object):

    def __init__(self, task_name, task_execution_fn, message_callback, update_progress_callback,
                 task_ended_callback):

        self.task_name = task_name

        self.execution_thread = None
        self.status = TaskStatuses.NOT_STARTED

        self.task_execution_fn = task_execution_fn

        self.message_cb = message_callback
        self.progress_cb = update_progress_callback
        self.task_ended_cb = task_ended_callback

    def _task_execution_wrapper(self, data, message_cb, update_progress_cb, task_ended_cb):

        try:
            self.status = self.task_execution_fn(data, message_cb, update_progress_cb, task_ended_cb,
                                                 TaskStatuses)
        except:
            self.status = TaskStatuses.ERRORED
            # TODO: handle exceptions properly here
            raise

    def _task_to_ui_message_wrapper(self, message_text, message_level):

        self.message_cb(self.task_name, message_text, message_level)

    def _task_to_ui_update_progress(self, percent_complete):

        self.progress_cb(self.task_name, percent_complete)

    def _task_to_ui_execution_finished(self, completion_status, completion_message):

        self.task_ended_cb(self.task_name, completion_status, completion_message)

    def start_task(self, input_data):

        self.message_cb(self.task_name, 'in start_task() for task: "%s"' % self.task_name, 'info')

        if self.status != TaskStatuses.WORKING:
            self.execution_thread = threading.Thread(target=self._task_execution_wrapper,
                                                     args=(input_data,
                                                           self._task_to_ui_message_wrapper,
                                                           self._task_to_ui_update_progress,
                                                           self._task_to_ui_execution_finished))
            self.status = TaskStatuses.WORKING
            self.execution_thread.start()
        else:
            self.message_cb(self.task_name, 'Task is already running.', 'warning')

    def get_status(self):

        return self.status

    def is_task_running(self):

        return self.status == TaskStatuses.WORKING


