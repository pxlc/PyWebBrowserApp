/*
+ ==============================================================================
|
|     TaskPlugin plugin JavaScript
|
+ ==============================================================================
*/

function ${P}() {
    let _self = this;

    _self.auto_init = function()  // put this in "base" class to always run as a standard mechanism
    {
        let reparent_el_list = document.querySelectorAll("[${P}-parent]");

        for (let c=0; c < reparent_el_list.length; c++)
        {
            let reparent_el = reparent_el_list[c];
            let target_parent_id = reparent_el.getAttribute("${P}-parent");
            let parent_el = document.getElementById(target_parent_id);

            if (parent_el) {
                parent_el.appendChild(reparent_el.parentNode.removeChild(reparent_el));
            } else {
                pwba.log_msg('ERROR: Plugin "' + _self.plugin_name + '" is not able to reparent ' +
                             'element with ID "' + reparent_el.id + '" ... no element with ID "' +
                             target_parent_id + '" defined in your App\'s HTML.');
            }
        }
    };

    _self.init = function()  // this is custom initialization for the specific plugin
    {
        pwba.log_msg('Custom initialization for "${P}" Plugin.');
    };

    _self.msg_levels = {
        INFO: 'info',
        DEBUG: 'debug',
        WARNING: 'warning',
        ERROR: 'error',
        CRITICAL: 'critical',
    };

    _self.test_fn = function()
    {
        alert('Hello from ${P}');
    };

    _self.to_html_safe_text = function (str) {
        return String(str).replace(/&/g, '&amp;')
                          .replace(/</g, '&lt;')
                          .replace(/>/g, '&gt;')
                          .replace(/"/g, '&quot;');
    };

    _self.msg_log_scroll_to_end = function()
    {
        let msg_log_div = document.getElementById("${P}_message_log");
        let children = msg_log_div.children;

        var total_height = 80; // add in some height to adjust for padding and such
        for (let c=0; c < children.length; c++ ) {
            total_height = total_height + children[c].offsetHeight;
        }
        msg_log_div.scrollTop = total_height;
    };

    _self.start_task = function(task_data) {
        _self.plugin_to_python('start_task', task_data);
    };

    _self.set_progress_bar_percentage = function(percent_complete) {
        let p_bar_div = document.getElementById("${P}_progress_bar_inner");
        p_bar_div.style.width = "" + percent_complete + "%";
    };

    _self._set_controls_active_state = function(is_active) {
        let control_el_list = document.getElementsByClassName("${P}_control");
        for (let c=0; c < control_el_list.length; c++) {
            if (is_active) {
                if ('disabled' in control_el_list[c]) {
                    control_el_list[c].removeAttribute('disabled');
                }
            } else {
                control_el_list[c].setAttribute('disabled', 'disabled');
            }
        }
    };

    _self.disable_controls = function() { _self._set_controls_active_state(false); };

    _self.enable_controls = function() { _self._set_controls_active_state(true); };

    // -------------------------------------------------------------------------------
    //
    //  Below are functions called from Python, so each of these only take one
    //  argument "op_data" that is a dictionary/object with any data to pass along
    //
    // -------------------------------------------------------------------------------
    _self.ui_update_progress = function(op_data) {
        _self.set_progress_bar_percentage(op_data.percent_complete);
    };

    _self.ui_disable_controls = function(op_data) {
        _self.disable_controls();
    };

    _self.ui_message = function(op_data) {
        let msg = op_data.message;
        let msg_level = op_data.message_level;

        let msg_level_class = "${P}_message_" + msg_level;

        if (msg_level == "info") {
            msg_line_prefix = "[INFO]: ";
        }
        else if (msg_level == "debug") {
            msg_line_prefix = "[DEBUG]: ";
        }
        else if (msg_level == "warn") {
            msg_line_prefix = "[WARNING]: ";
        }
        else if (msg_level == "error") {
            msg_line_prefix = "[ERROR]: ";
        }
        else if (msg_level == "critical") {
            msg_line_prefix = "[CRITICAL]: ";
        }
        else {
            msg_line_prefix = "[???]: ";
        }

        let msg_log_div = document.getElementById("${P}_message_log");

        let msg_lines = msg.split('\n');

        for (let c=0; c < msg_lines.length; c++) {
            // output each line
            let m_line = msg_lines[c];
            if (c == 0)
                m_line = msg_line_prefix + m_line;

            let html_str = '<span class="' + msg_level_class +'">' + _self.to_html_safe_text(m_line) +
                            "</span><br/>";

            msg_log_div.insertAdjacentHTML('beforeend', html_str);
        }
        _self.msg_log_scroll_to_end();
    };

    _self.ui_task_ended = function(op_data) {
        _self.set_progress_bar_percentage(100.0);
        _self.msg_log_scroll_to_end();
        _self.enable_controls();

        setTimeout(function() {
            alert("Task completed with status '" + op_data.completion_status + '" and message "' +
                  op_data.completion_message + '"')
        }, 100);
    };
}

pwba.register_plugin_js(${P});


