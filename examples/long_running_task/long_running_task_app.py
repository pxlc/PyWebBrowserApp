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
import time
import logging

try:
    from PyWebBrowserApp import PyWebBrowserAppBase, register_op
except:
    # if import fails try import from package name that is all lowercase
    from pywebbrowserapp import PyWebBrowserAppBase, register_op

PYWEBBROWSERAPP_ROOT = os.environ['PYWEBBROWSERAPP_ROOT']


def directory_listing_task(data, ui_message_fn, ui_update_progress_fn, ui_task_ended_fn, task_statuses):

    folder_path = data.get('folder_path', '')

    starting_msg = '\n'.join([
        '',
        '---------------------------------------------------',
        '  Starting Processing for folder path:',
        '    %s' % folder_path,
        '---------------------------------------------------',
        '',
    ])
    ui_message_fn(starting_msg, 'info')
    ui_update_progress_fn(0)

    item_list = sorted(os.listdir(folder_path))
    num_items = len(item_list)

    for idx, item in enumerate(item_list):
        item_path = '%s/%s' % (folder_path, item)
        ui_message_fn('>> Processing folder item: %s' % item, 'info')

        time.sleep(1)

        if os.path.isfile(item_path):
            ui_message_fn('   ... is a File', 'info')
        elif os.path.isdir(item_path):
            ui_message_fn('   ... is a Directory', 'info')
        else:
            ui_message_fn('   ... is a ????', 'info')

        percent_complete = int((float(idx+1) / float(num_items)) * 100.0 + 0.5) 
        ui_update_progress_fn(percent_complete)

    completion_msg = '\n'.join([
        '',
        '---------------------------------------------------',
        '  Processing of folder path:',
        '    %s' % folder_path,
        '  ... COMPLETED.',
        '---------------------------------------------------',
    ])
    ui_message_fn(completion_msg, 'info')
    ui_task_ended_fn('ok', 'processing completed successfully')

    return task_statuses.COMPLETED


class CustomPyWebBrowserApp(PyWebBrowserAppBase):

    def __init__(self, app_module_path, width=800, height=600,
                 start_html_filename='', template_dirpath='', config_filepath='',
                 log_to_shell=False, log_level_str=''):

        super(CustomPyWebBrowserApp, self).__init__(app_module_path, width=width, height=height,
                                                    template_dirpath=template_dirpath,
                                                    start_html_filename=start_html_filename,
                                                    config_filepath=config_filepath,
                                                    log_to_shell=log_to_shell,
                                                    log_level_str=log_level_str)

        # Do any required data set-up for your app here
        self.add_task('DirectoryListing', directory_listing_task)

    # --------------------------------------------------------------------------------------------------------
    # "setup_extra_template_vars()" is a REQUIRED override method
    #
    #  Establish any values for template vars in this method that you need to use in your HTML template file.
    # --------------------------------------------------------------------------------------------------------
    def setup_extra_template_vars(self):

        app_window_title = 'Long Running Task'
        app_header = '%s Example' % app_window_title

        res_icon_path = '%s/res/icons' % PYWEBBROWSERAPP_ROOT

        extra_vars = {
            'RES_ICON_PATH': res_icon_path.replace('\\', '/'),
            'APP_WINDOW_TITLE': app_window_title,
            'APP_HEADER': app_header,
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

    @register_op
    def process_folder_path(self, op_data):

        self.info('')
        self.info(':: got op "process_folder_path" with data "{0}"'.format(op_data))
        self.info('')

        if self.is_task_running('DirectoryListing'):
            # a thread is live still
            self.send_to_webbrowser('popup_message', {
                'title': 'Warning',
                'message': 'Long running task is in progress. Cannot start another task process.'
            })
            return

        folder_path = os.path.expandvars(op_data.get('folder_path', '')).strip().replace('\\', '/')

        if not folder_path or not os.path.exists(folder_path):
            self.send_to_webbrowser('popup_message', {
                'title': 'Error',
                'message': 'Folder path "' + folder_path + '" is empty or does not exist.'
            })
            return

        if not os.path.isdir(folder_path):
            self.send_to_webbrowser('popup_message', {
                'title': 'Error',
                'message': 'Folder path "' + folder_path + '" is not a directory.'
            })
            return

        self.start_task('DirectoryListing', {'folder_path': folder_path})

