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
import getopt
import logging
import importlib


def launch_app(app_module_path, shell_logging=False, log_level_str='ERROR', config_filepath='',
               template_filepath='', width=0, height=0):

    app_module_name = os.path.basename(app_module_path).replace('.py','')
    app_dir_path = os.path.dirname(app_module_path).replace('\\', '/')

    start_html_filename = ''
    template_dir_path = ''

    if template_filepath:
        template_dir_path = os.path.dirname(template_filepath).replace('\\', '/')
        start_html_filename = os.path.basename(template_filepath)

    sys.path.append(app_dir_path)
    app_module = importlib.import_module(app_module_name)

    options = {
        'start_html_filename': start_html_filename,
        'template_dirpath': template_dir_path,
        'config_filepath': config_filepath,
        'log_to_shell': shell_logging,
        'log_level_str': log_level_str,
    }

    if width:
        options['width'] = width
    if height:
        options['height'] = height

    app = app_module.CustomPyWebBrowserApp(app_module_path, **options)
    app.launch()


