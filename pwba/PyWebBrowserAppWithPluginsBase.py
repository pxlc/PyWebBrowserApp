
import os
import re
import sys
import json
import importlib

from .PyWebBrowserAppBase import PyWebBrowserAppBase


def register_plugin_op(plugin_op_method):

    def registered_plugin_op_method(self, op_data):
        plugin_op_method(self, op_data)

    registered_plugin_op_method._plugin_op_method = str(plugin_op_method).split()[1]
    return registered_plugin_op_method


class PyWebBrowserAppWithPluginsBase(PyWebBrowserAppBase):

    CFG_TOKEN_PATTERN = r'(\${[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+})' # NOTE: must escape $ character
    CFG_TOKEN_REGEX = re.compile(CFG_TOKEN_PATTERN)

    PLUGIN_HTML_TEMPLATE = '''
<!-- Plugin: {PLUGIN_NAME} (START) -->
<script language="JavaScript">
{PLUGIN_JS}
</script>
<style>
{PLUGIN_CSS}
</style>
<div id="PWBA_{PLUGIN_NAME}">
{PLUGIN_CONTENT_HTML}
</div>
<!-- Plugin: {PLUGIN_NAME} (END) -->
'''

    def __init__(self, app_module_filepath, webbrowser_path='', width=480, height=600, template_dirpath='',
                 start_html_filename='', config_filepath='', log_to_shell=False, log_level_str='',
                 app_temp_root='', webbrowser_data_path=''):

        super(PyWebBrowserAppWithPluginsBase, self).__init__(app_module_filepath, width=width, height=height,
                                                             template_dirpath=template_dirpath,
                                                             start_html_filename=start_html_filename,
                                                             config_filepath=config_filepath,
                                                             log_to_shell=log_to_shell,
                                                             log_level_str=log_level_str,
                                                             app_temp_root=app_temp_root,
                                                             webbrowser_data_path=webbrowser_data_path)

        self.active_plugins_root = os.path.join(self.app_temp_root, 'plugins_%s' % self.session_id)

        self.plugin_list = []
        self.plugin_info_by_name = {}
        self.plugin_instance_by_name = {}

        self.search_path_list = []
        if 'PWBA_PLUGINS_PATH' in os.environ:
            env_search_paths = [p.strip() for p in os.environ.get('PWBA_PLUGINS_PATH', '').split(os.pathsep)
                                if p.strip()]
            self.search_path_list += env_search_paths
        self.search_path_list.append('%s/plugins' % self.PYWEBBROWSERAPP_ROOT)

    def _setup_plugin_op_handlers(self):

        # set up callbacks here
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if 'bound method' in str(attr) and hasattr(attr, '_op_name'):
                op_name = attr._op_name.split('.')[1] if '.' in attr._op_name else attr._op_name
                print('    adding op: %s' % op_name)
                self.add_op_handler(op_name, attr)

    def request_plugin(self, plugin_name, variation='default'):

        self.plugin_list.append(plugin_name)
        self.plugin_info_by_name[plugin_name] = {}

        # first find path to plugin in search paths
        plugin_path = ''
        for p in self.search_path_list:
            path_to_test = '%s/%s' % (p, plugin_name)
            if os.path.exists(path_to_test):
                plugin_path = path_to_test
                break

        if not plugin_path:
            self.error('Plugin "%s" not found in any of the Plugins Search Paths ... unable to load plugin.' %
                       plugin_name)
            del self.plugin_info_by_name[plugin_name]
            return

        info_pairs = [
            ('html_path', '%s/pwba_plugin.html' % plugin_path),
            ('css_path', '%s/pwba_plugin.css' % plugin_path),
            ('js_path', '%s/pwba_plugin.js' % plugin_path),
            ('py_path', '%s/pwba_plugin.py' % plugin_path),
        ]

        for (info_key, info_value) in info_pairs:
            if os.path.exists(info_value):
                self.plugin_info_by_name[plugin_name][info_key] = info_value

        # load plugin config
        config = {}
        cfg_filepath = '%s/pwba_plugin_config.json' % plugin_path
        if os.path.exists(cfg_filepath):
            with open(cfg_filepath, 'r') as fp:
                full_config = json.load(fp)
            if variation not in full_config:
                self.error('Variation "%s" not defined in config for Plugin "%s" ... unable to load plugin.' %
                        (varation, plugin_name))
                del self.plugin_info_by_name[plugin_name]
                return
            config = full_config[variation]
        self.plugin_info_by_name[plugin_name]['config'] = config

        if 'py_path' in self.plugin_info_by_name[plugin_name]:
            self.load_python_plugin_code(plugin_name, self.plugin_info_by_name[plugin_name]['py_path'])

    def _convert_component_file(self, plugin_name, component_filepath, plugin_config):

        converted_lines = []
        with open(component_filepath, 'r') as fp:
            for line in fp:
                # first change all ${P} occurrences
                line = line.replace('${P}', plugin_name)
                # then replace tokens based on config
                cfg_tokens = self.CFG_TOKEN_REGEX.findall(line)
                for ctok in cfg_tokens:
                    try:
                        (scope, param) = ctok.replace('${', '').replace('}', '').split('.')
                    except:
                        self.warning('Unable to decode token "%s" in "%s" component' % (ctok, component_filepath))
                        continue
                    try:
                        replace_value = plugin_config[scope][param]
                    except:
                        self.warning('Token "%s" not defined in Plugin config (referenced in "%s" component)' % (ctok, component_filepath))
                        continue
                    line = line.replace(ctok, replace_value.replace('${P}', plugin_name))

                converted_lines.append(line.rstrip())

        return '\n'.join(converted_lines)

    def generate_html_file(self, template_filename):

        # now go through all plugins and build the html from all of the html components that each plugin needs to
        # add to the body HTML ... all of the plugin html will be added as children at the end of the <body> block

        all_plugins_html_list = []

        for plugin_name in self.plugin_list:
            p_info = self.plugin_info_by_name[plugin_name]

            print('')
            print('p_info: %s' % json.dumps(p_info, indent=4, sort_keys=True))
            print('')

            if not p_info:
                self.warning('Plugin "%s" does not have any content ... not adding plugin to app.' % plugin_name)
                continue

            p_cfg = self.plugin_info_by_name[plugin_name]['config']

            p_html_str = ''
            p_css_str = ''
            p_js_str = ''

            if 'html_path' in p_info:
                p_html_str = self._convert_component_file(plugin_name, p_info['html_path'], p_cfg)
            if 'css_path' in p_info:
                p_css_str = self._convert_component_file(plugin_name, p_info['css_path'], p_cfg)
            if 'js_path' in p_info:
                p_js_str = self._convert_component_file(plugin_name, p_info['js_path'], p_cfg)

            all_plugins_html_list.append(self.PLUGIN_HTML_TEMPLATE.format(
                PLUGIN_CONTENT_HTML=p_html_str, PLUGIN_CSS=p_css_str, PLUGIN_JS=p_js_str, PLUGIN_NAME=plugin_name
            ))

        all_plugins_html = '\n'.join(all_plugins_html_list)

        # print('')
        # print(all_plugins_html)
        # print('')

        return super(PyWebBrowserAppWithPluginsBase, self).generate_html_file(template_filename, all_plugins_html)

    def load_python_plugin_code(self, plugin_name, src_plugin_path):

        active_plugin_dir_path = os.path.join(self.active_plugins_root, plugin_name)

        os.makedirs(active_plugin_dir_path)
        sys.path.insert(0, active_plugin_dir_path)

        plugin_module_name = 'PWBA%s' % plugin_name
        plugin_module_filepath = os.path.join(active_plugin_dir_path, '%s.py' % plugin_module_name)

        with open(src_plugin_path, 'r') as fp:
            src_text = fp.read()
        with open(plugin_module_filepath, 'w') as fp:
            fp.write(src_text.replace('${P}', plugin_name))

        plugin_module = importlib.import_module(plugin_module_name)

        plugin_instance = plugin_module.PluginSubclass()
        plugin_instance._setup_logging_functions(self.debug, self.info, self.warning, self.error, self.critical)

        self.plugin_instance_by_name[plugin_name] = plugin_instance

        for attr_name in dir(plugin_instance):
            attr = getattr(plugin_instance, attr_name)
            if 'bound method' in str(attr) and hasattr(attr, '_plugin_op_method'):
                op_method = attr._plugin_op_method.split('.')[1] if '.' in attr._plugin_op_method else attr._plugin_op_method
                op_name = '%s_%s' % (plugin_name, op_method)
                print('    adding op: %s' % op_name)
                self.add_op_handler(op_name, attr)

