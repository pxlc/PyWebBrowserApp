
function ${P}() {
    let _self = this;

    _self.outer_div = null;

    _self.init = function()  // this is custom initialization for the specific plugin
    {
    };

    _self.show = function()
    {
        if (! _self.outer_div) {
            _self.outer_div = document.getElementById("id_${P}_outer");
        }
        _self.outer_div.style.display = "block";
    };

    _self.hide = function()
    {
        if (! _self.outer_div) {
            _self.outer_div = document.getElementById("id_${P}_outer");
        }
        _self.outer_div.style.display = "none";
    };

    _self.validate_dirpath = function(dirpath_to_validate, callback_fn_name)
    {
        console.log(':: inside pwba.${P}.validate_dirpath() function!');

        _self.plugin_to_python("validate_dirpath", {"dirpath_to_validate": dirpath_to_validate,
                                                    "callback_fn_name": callback_fn_name});
    };
    
    _self.response_to_validate_dirpath = function(op_data)
    {
        let is_path_valid = op_data.is_path_valid;
        let validation_callback_fn_name = op_data.callback_fn_name;
        let dir_items_info = op_data.dir_items_info;

        if (validation_callback_fn_name) {
            let exec_str = validation_callback_fn_name + '(is_path_valid, dir_items_info);';
            eval(exec_str);
        }
    };

    _self.get_path_value = function()
    {
        let path_value = document.getElementById("id_${P}_pathEdit").value;
        return path_value;
    };

    _self.set_path_value = function(new_path_value)
    {
        let path_text_input_el = document.getElementById("id_${P}_pathEdit");
        path_text_input_el.value = new_path_value;
    };

    _self.apply_path_input_validation = function(is_path_valid, dir_items_info)
    {
        let path_text_input_el = document.getElementById("id_${P}_pathEdit");
        path_text_input_el.classList.remove("${P}_error", "${P}_success");
        if (is_path_valid) {
            path_text_input_el.classList.add("${P}_success");
            console.log(dir_items_info)
        } else {
            path_text_input_el.classList.add("${P}_error");
        }
    };
}

//
// NOTE: Here is how you get a callback setup to run once the document is ready (and all DOM elements are available)
//
document.addEventListener('DOMContentLoaded', (event) => {
    //the event occurred
    console.log(':: EXECUTING onload callback for ENTER key.');

    let path_edit_el = document.getElementById("id_${P}_pathEdit");
    path_edit_el.onkeyup = function(e) {
        if (e.key === 'Enter' || e.code === 13) {
            let path_value = pwba.${P}.get_path_value();
            if (path_value) {
                pwba.${P}.validate_dirpath(path_value, "pwba.${P}.apply_path_input_validation");
            }
        }
    };
    path_edit_el.onblur = function(e) {
        let path_value = pwba.${P}.get_path_value();
        if (path_value) {
            pwba.${P}.validate_dirpath(path_value, "pwba.${P}.apply_path_input_validation");
        }
    };
});

pwba.register_plugin_js(${P});
