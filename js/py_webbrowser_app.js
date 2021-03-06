// -------------------------------------------------------------------------------
// MIT License
//
// Copyright (c) 2018 pxlc@github
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
// -------------------------------------------------------------------------------

function object_to_str(obj)
{
    let key_var_strs = [];

    const keys = Object.keys(obj);
    keys.forEach((key, index) => {
        if (typeof(obj[key]) == "string") {
            key_var_strs.push(`"${key}": "${obj[key]}"`);
        } else {
            key_var_strs.push(`"${key}": "${obj[key]}"`);
        }
    })

    return "{" + key_var_strs.join(", ") + "}";
}


//
// definition of "Class" PyWebBrowserApp (via function declaration)
//
function PyWebBrowserApp()
{
    let _self = this;

    _self.session_id = null;
    _self.port_num = null;
    _self.onappready_callback_fn = null;
    _self.app_is_ready = false;
    _self.app_data_receiver_by_op = {};

    _self.active_plugins = [];

    _self.ws = null;
    _self.connection_made = false;

    // ======================================================================================
    // [ start of API calls ]
    //
    _self.init = function(session_id, port_num) {
        _self.session_id = session_id;
        _self.port_num = port_num;

        // Connect to Web Socket
        _self.ws = new WebSocket("ws://localhost:" + _self.port_num + "/");

        // Set event handlers.
        _self.ws.onopen = function() {
            _self.log_msg("onopen");
            _self.app_is_ready = true;
        };
    
        // receiver of messages from Python
        _self.ws.onmessage = function(e) {
            // IMPORTANT: don't try/catch this so that detailed Javascript error will show up in inspector if
            //            an exception is thrown that you can click through to see the code.
            let data = JSON.parse(e.data);
            _self.data_receiver(data);
        };
    
        _self.ws.onclose = function() {
            _self.log_msg("onclose");
        };

        _self.ws.onerror = function(e) {
            _self.log_msg("onerror");
            console.log(e)
        };

        _self.close = function() {
            _self.ws.close();
        };
    };

    _self.init_plugins = function() {
        for (let c=0; c < _self.active_plugins.length; c++) {
            let plugin_name = _self.active_plugins[c];
            let plugin_instance = _self[plugin_name];

            // run auto_init for standard Plugin mechanisms first
            if ('auto_init' in plugin_instance) {
                plugin_instance['auto_init']();
            }

            // then run init for custom Plugin initialization for the specific plugin
            if ('init' in plugin_instance) {
                plugin_instance['init']();
            }
        }
    };

    _self.is_app_ready = function() { return _self.app_is_ready; };

    _self.get_session_id = function() { return _self.session_id; };
    _self.get_port_num = function() { return _self.port_num; };

    _self.pyprint = function(message) {
        // this function allows you to print messages to the python session side of the app
        // which will show up in the app log file
        _self.to_python("PyWebBrowserApp_print_message", {"message": "" + message});
    };

    _self.log_msg = function(message) {
        let prefixed_message = "[JS] " + message
        _self.pyprint(prefixed_message);
        console.log(message);
    };

    _self.data_receiver = function(received_data)
    {
        // this is where you receive calls from the python side of your PyChromiumApp
        let op = received_data.op;
        let op_data = received_data.data;
        let session_id = received_data.session_id;

        let op_data_str = object_to_str(op_data);

        if (session_id != _self.session_id) {
            // Should really never get here, but just a sanity check
            alert("Data received did not have correct session ID. Ignoring data.");
            return;
        }

        if (!_self.session_id || !_self.port_num) {
            // I think it would not get here if the session wasn't initialized
            alert("PyWebBrowserApp JavaScript session has not yet been initialized. Unable to " +
                  "execute op handler.");
            return;
        }
    
        if (op == "connection_status") {
            if (op_data.status == "CONNECTED") {
                _self.log_msg("Web Browser front-end of PyWebBrowserApp is READY!");

                // initialize plugins here, as we have a connection established
                if (_self.active_plugins.length) {
                    _self.init_plugins();
                }

                if (_self.onappready_callback_fn) {
                    _self.onappready_callback_fn();
                }
            } else {
                _self.log_msg("WARNING: NOT CONNECTED YET ... Web Browser front-end of PyWebBrowserApp got " +
                              "connection status of '" + op_data.status + "'!");
            }
            return;
        }

        // Check for and handle any Plugin ops
        if (op.startsWith('Plugin|'))
        {
            let tokens = op.split('|');  // op e.g. "Plugin|MyFirstPlugin|test_fn"
            let plugin_name = tokens[1];
            let plugin_function_name = tokens[2];

            if ( !(plugin_name in _self) ) {
                _self.log_msg('ERROR: Plugin "' + plugin_name + '" was not registered (or failed to ' +
                              'register) ... plugin op "' + op + '" cannot be delegated to a plugin function.');
                return;
            }

            let plugin_instance = _self[plugin_name];
            if ( !(plugin_function_name in plugin_instance) ) {
                _self.log_msg('ERROR: Plugin "' + plugin_name + '" instance does not have the requested ' +
                              'function "' + plugin_function_name + '" ... op cannot be delegated to ' +
                              'be handled.');
                return;
            }

            let plugin_fn = _self[plugin_name][plugin_function_name];

            // delegate the operation to Plugin's function
            plugin_fn(op_data);
            return;
        }

        // Check for and handle any Task ops
        if (op.startsWith('PyWebBrowserApp_task_')) {
            let task_name = op_data.task_name;
            if (!(task_name in _self.task_ui_calls_by_name)) {
                // callbacks not registered for this given task_name
                _self.pyprint('WARNING: Callbacks have not been registered for Task name "' +
                                task_name + '" - unable to handle op "' + op + '"');
                return;
            }

            // Task UI callback function signatures:
            //
            //     message_fn(message_lines, message_level);
            //
            //     update_progress_fn(percent_complete);  // this is a number between 0 and 100
            //
            //     task_ended_fn(completion_status, completion_message);
            //
            if (op.endsWith('_to_ui_message')) {
                _self.task_ui_calls_by_name[task_name].message_fn(op_data.msg_lines, op_data.msg_level);
            }
            else if (op.endsWith('_to_ui_update_progress')) {
                _self.task_ui_calls_by_name[task_name].update_progress_fn(op_data.percent_complete);
            }
            else if (op.endsWith('_to_ui_execution_finished')) {
                _self.task_ui_calls_by_name[task_name].task_ended_fn(op_data.status, op_data.message);
            }
            else {
                _self.pyprint('WARNING: Unknown op "' + op + '" called for Task name "' + task_name +
                              '" - unable to process op');
            }
            return;
        }

        if (op in _self.app_data_receiver_by_op) {
            var data_receiver_fn = _self.app_data_receiver_by_op[op];
            data_receiver_fn(op_data);
        } else {
            var msg = 'WARNING: Op "' + op + '" does NOT have a registered data receiver ' +
                      'handler function.';
            _self.log_msg(msg);
        }
    };

    _self.register_op_handler = function(op, op_handler_fn) {
        _self.app_data_receiver_by_op[op] = op_handler_fn;
    };

    // TRANSITION: previously named "register_onopen_callback()"
    //
    _self.register_onappready_callback = function(onappready_callback_fn) {
        _self.onappready_callback_fn = onappready_callback_fn;
    };

    _self.register_plugin_js = function(plugin_function_class) {
        let plugin_instance = new plugin_function_class();
        let plugin_name = plugin_instance.constructor.name;

        plugin_instance.plugin_name = plugin_name
        plugin_instance.plugin_to_python = function(plugin_op, plugin_op_data) {
            pwba._plugin_to_python(plugin_name, plugin_op, plugin_op_data);
        };

        // --------------------------------------------------------------------------------------------
        // Mechanism to reparent any HTML elements in the pwba_plugin.html file ... how this works is
        // --------------------------------------------------------------------------------------------
        //
        // (1) Any HTML elements in the pwba_plugin.html file that you want to reparent you need to add
        //     a `${P}-parent="${P}_some_element_id"` as an attribute on that element.
        //
        // (2) In your app's HTML template make sure to use the value of the above new attribute
        //     (e.g. "${P}_some_element_id"), but replacing the "${P}" part with the actual name of
        //     the plugin (e.g. "MyFirstPlugin_some_element_id"), as the ID for the element to reparent
        //     the HTML element in (1) above as a child node to be appended at the end.
        //
        plugin_instance.auto_init = function()
        {
            let plugin_name = plugin_instance.plugin_name;
            let reparent_el_list = document.querySelectorAll("[" + plugin_name + "-parent]");

            for (let c=0; c < reparent_el_list.length; c++)
            {
                let reparent_el = reparent_el_list[c];
                let target_parent_id = reparent_el.getAttribute(plugin_name + "-parent");
                let parent_el = document.getElementById(target_parent_id);

                if (parent_el) {
                    parent_el.appendChild(reparent_el.parentNode.removeChild(reparent_el));
                } else {
                    pwba.log_msg('ERROR: Plugin "' + plugin_name + '" is not able to reparent ' +
                                 'element with ID "' + reparent_el.id + '" ... no element with ID "' +
                                 target_parent_id + '" defined in your App\'s HTML.');
                }
            }
        };

        _self.active_plugins.push(plugin_name);

        _self[plugin_name] = plugin_instance;
    };

    // message sender - sends data to Python
    _self.to_python = function(op, data) {
        var msg_data = {
            "op": op,
            "session_id": _self.session_id,
            "data": data
        }
        var msg_data_str = JSON.stringify(msg_data);
        _self.ws.send(msg_data_str);
        return msg_data_str;
    };

    _self._plugin_to_python = function(plugin_name, op, data) {
        var msg_data = {
            "op": plugin_name + "_" + op,
            "session_id": _self.session_id,
            "data": data
        }
        var msg_data_str = JSON.stringify(msg_data);
        _self.ws.send(msg_data_str);
        return msg_data_str;
    };

    _self.task_ui_calls_by_name = {};

    // Task callback function signatures:
    //
    //     message_fn(msg_lines, msg_level);
    //
    //     update_progress_fn(percent_complete);  // this is a number between 0 and 100
    //
    //     task_ended_fn(completion_status, completion_message);
    //
    _self.register_task = function(task_name, message_fn, update_progress_fn, task_ended_fn) {
        _self.task_ui_calls_by_name[task_name] = {
            'message_fn': message_fn,
            'update_progress_fn': update_progress_fn,
            'task_ended_fn': task_ended_fn,
        };
    };

    // [ end of API calls ]
    // ======================================================================================

    // Utility methods
    _self.sanitize_string_for_html = function(text) {
        var element = document.createElement('div');
        element.innerText = text;
        return element.innerHTML;
    };
}

//
// Instantiate global JavaScript session instance of PyWebBrowserApp "Class"
//
var pwba = new PyWebBrowserApp();

