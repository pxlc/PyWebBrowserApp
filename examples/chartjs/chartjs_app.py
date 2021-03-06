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
import logging

try:
    from PyWebBrowserApp import PyWebBrowserAppBase, register_op
except:
    # if import fails try import from package name that is all lowercase
    from pywebbrowserapp import PyWebBrowserAppBase, register_op

PYWEBBROWSERAPP_ROOT = os.environ['PYWEBBROWSERAPP_ROOT']


class CustomPyWebBrowserApp(PyWebBrowserAppBase):

    def __init__(self, app_module_path, width=480, height=600,
                 start_html_filename='', template_dirpath='', config_filepath='',
                 log_to_shell=False, log_level_str='', webbrowser_path='', on_start_options_d=None):

        super(CustomPyWebBrowserApp, self).__init__(app_module_path, width=width, height=height,
                                                    template_dirpath=template_dirpath,
                                                    start_html_filename=start_html_filename,
                                                    config_filepath=config_filepath,
                                                    log_to_shell=log_to_shell,
                                                    log_level_str=log_level_str,
                                                    webbrowser_path=webbrowser_path,
                                                    on_start_options_d=on_start_options_d)

        # Do any required data set-up for your app here
        pass

    # --------------------------------------------------------------------------------------------------------
    # "setup_extra_template_vars()" is a REQUIRED override method
    #
    #  Establish any values for template vars in this method that you need to use in your HTML template file.
    # --------------------------------------------------------------------------------------------------------
    def setup_extra_template_vars(self):

        res_image_path = os.path.realpath( os.path.join(PYWEBBROWSERAPP_ROOT, 'res', 'images') )
        res_icon_path = os.path.realpath( os.path.join(PYWEBBROWSERAPP_ROOT, 'res', 'icons') )

        extra_vars = {
            'RES_IMG_PATH': res_image_path.replace('\\', '/'),
            'RES_ICON_PATH': res_icon_path.replace('\\', '/'),
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


