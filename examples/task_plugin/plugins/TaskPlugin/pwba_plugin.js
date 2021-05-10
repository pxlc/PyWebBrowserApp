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
    }

    _self.msg_log_scroll_to_end = function()
    {
        let msg_log_div = document.getElementById("${P}_message_log");
        let children = msg_log_div.children;

        var total_height = 80; // add in some height to adjust for padding and such
        for (let c=0; c < children.length; c++ ) {
            total_height = total_height + children[c].offsetHeight;
        }
        msg_log_div.scrollTop(total_height);
    }

    /*
    function set_progress_bar_percentage(percent_int) {
        var p_bar_div = $("#progress_bar");
        p_bar_div.prop("aria-valuenow", "" + percent_int);
        p_bar_div.css("width", "" + percent_int + "%");
    }
    */

    _self.ui_message = function(op_data) {
        let msg = op_data.message;
        let msg_level = op_data.message_level;

        let msg_level_color = "blue";
        let msg_line_prefix = "[INFO]: ";

        if (msg_level == "debug") {
            msg_level_color = "green";
            msg_line_prefix = "[DEBUG]: ";
        }
        else if (msg_level == "warn") {
            msg_level_color = "orange";
            msg_line_prefix = "[WARNING]: ";
        }
        else if (msg_level == "error") {
            msg_level_color = "red";
            msg_line_prefix = "[ERROR]: ";
        }

        let msg_log_div = document.getElementById("${P}_message_log");

        let msg_lines = msg.split('\n');

        for (let c=0; c < msg_lines.length; c++) {
            // output each line
            let m_line = msg_lines[c];
            if (c == 0)
                m_line = msg_line_prefix + m_line;

            let html_str = '<span style="color: ' + msg_level_color +';">' + _self.to_html_safe_text(m_line) +
                            "</span><br/>";

            msg_log_div.append(html_str);
        }
        _self.msg_log_scroll_to_end();
    }
}

pwba.register_plugin_js(${P});


