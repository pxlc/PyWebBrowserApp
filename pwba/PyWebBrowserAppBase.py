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

from .PyWebBrowserAppWithPluginsBase import PyWebBrowserAppWithPluginsBase


class PyWebBrowserAppBase(PyWebBrowserAppWithPluginsBase):

    def __init__(self, app_module_filepath, webbrowser_path='', width=480, height=600, template_dirpath='',
                 start_html_filename='', config_filepath='', log_to_shell=False, log_level_str='',
                 app_temp_root='', webbrowser_data_path='', on_start_options_d=None):

        super(PyWebBrowserAppBase, self).__init__(app_module_filepath, width=width, height=height,
                                                  template_dirpath=template_dirpath,
                                                  start_html_filename=start_html_filename,
                                                  config_filepath=config_filepath,
                                                  log_to_shell=log_to_shell,
                                                  log_level_str=log_level_str,
                                                  app_temp_root=app_temp_root,
                                                  webbrowser_path=webbrowser_path,
                                                  webbrowser_data_path=webbrowser_data_path)

        self._on_start_options_d = on_start_options_d

    def has_on_start_option(self, option_key):

        if (self._on_start_options_d):
            return self._on_start_options_d.has_key(option_key)
        return False

    def get_on_start_option(self, option_key):

        if (self._on_start_options_d):
            return self._on_start_options_d.get(option_key)
        return None

