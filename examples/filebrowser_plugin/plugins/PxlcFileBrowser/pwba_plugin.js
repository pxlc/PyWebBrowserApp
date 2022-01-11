
function ${P}() {
    let _self = this;

    _self.last_valid_path = '';
    _self.outer_div = null;

    _self.init = function()  // this is custom initialization for the specific plugin
    {
    };

    _self.show = function(dialog_title, open_btn_label, filename_edit_mode)
    {
        if (! dialog_title)
            dialog_title = 'File Browser';
        document.getElementById('id_${P}_dialog_title').innerHTML = pwba.sanitize_string_for_html(dialog_title);

        if (! open_btn_label)
            open_btn_label = 'Open';
        document.getElementById('id_${P}_open_btn').innerHTML = pwba.sanitize_string_for_html(open_btn_label);

        //
        // filename_edit_modes: 'allow_edit', 'display_only', 'hidden'
        //
        let filename_div_el = document.getElementById('id_${P}_filename_div');
        let filename_edit_el = document.getElementById('id_${P}_filenameEdit');

        if (filename_edit_mode == 'allow_edit') {
            filename_edit_el.removeAttribute('readonly');
            filename_edit_el.removeAttribute('disabled');
            filename_div_el.style.display = 'block';
        }
        else if (filename_edit_mode == 'display_only')
        {
            filename_edit_el.setAttribute('readonly', true);
            filename_edit_el.setAttribute('disabled', true);
            filename_div_el.style.display = 'block';
        }
        else {
            // otherwise assume 'hidden' mode
            filename_edit_el.setAttribute('readonly', true);
            filename_edit_el.setAttribute('disabled', true);
            filename_div_el.style.display = 'none';
        }

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
        let dirpath_value = op_data.dirpath_value;
        let is_path_valid = op_data.is_path_valid;
        let validation_callback_fn_name = op_data.callback_fn_name;
        let dir_items_info = op_data.dir_items_info;

        if (validation_callback_fn_name) {
            let exec_str = validation_callback_fn_name + '(dirpath_value, is_path_valid, dir_items_info);';
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

    _self.apply_path_input_validation = function(dirpath_value, is_path_valid, dir_items_info)
    {
        let path_text_input_el = document.getElementById("id_${P}_pathEdit");
        path_text_input_el.value = dirpath_value;

        path_text_input_el.classList.remove("${P}_error", "${P}_success");

        if (is_path_valid && dir_items_info) {
            _self.last_valid_path = dirpath_value;
            path_text_input_el.classList.add("${P}_success");
            _self.fill_folders_listing(dir_items_info.folders);
            _self.fill_files_listing(dir_items_info.files);
        } else {
            _self.last_valid_path = '';
            path_text_input_el.classList.add("${P}_error");
            _self.clear_folders_listing();
            _self.clear_files_listing();
        }
    };

    _self.clear_folders_listing = function() {
        let folder_listing_ul_el = document.getElementById('id_${P}_navArea_foldersListing');
        folder_listing_ul_el.innerHTML = '';
    };

    _self.fill_folders_listing = function(folder_list)
    {
        let folder_listing_div_el = document.getElementById('id_${P}_navArea_foldersListing');

        let html_str_list = [
            '<ul class="${P}_folder_listing">',
            '<li class="${P}_item ${P}_no_text_select" ondblclick="pwba.${P}.go_up_one_dir();">..</li>'
        ];

        for (var c=0; c < folder_list.length; c++) {
            let safe_foldername = pwba.sanitize_string_for_html(folder_list[c]);
            html_str_list.push('<li class="${P}_item ${P}_no_text_select" title="' + safe_foldername + '"' +
                                'ondblclick="pwba.${P}.select_folder_item(this);">' + safe_foldername + '</li>');
        }
        html_str_list.push('</ul>');

        folder_listing_div_el.innerHTML = html_str_list.join('\n');

        let li_list = folder_listing_div_el.querySelectorAll('li');
        for (var c=1; c < li_list.length; c++) {
            let li_el = li_list[c];
            li_el._original_foldername = folder_list[c-1];
        }
    };

    _self.clear_files_listing = function() {
        let files_listing_ul_el = document.getElementById('id_${P}_navArea_filesListing');
        files_listing_ul_el.innerHTML = '';
    };

    _self.fill_files_listing = function(file_list)
    {
        let files_listing_div_el = document.getElementById('id_${P}_navArea_filesListing');

        let html_str_list = ['<ul class="${P}_file_listing">'];
        for (var c=0; c < file_list.length; c++) {
            let safe_filename = pwba.sanitize_string_for_html(file_list[c]);
            html_str_list.push('<li class="${P}_item ${P}_no_text_select" title="' + safe_filename + '"' +
                                'onclick="pwba.${P}.select_file_item(this);">' + safe_filename + '</li>');
        }
        html_str_list.push('</ul>');

        files_listing_div_el.innerHTML = html_str_list.join('\n');

        let li_list = files_listing_div_el.querySelectorAll('li');
        for (var c=0; c < li_list.length; c++) {
            let li_el = li_list[c];
            li_el._original_filename = file_list[c];
        }
    };

    _self.go_up_one_dir = function()
    {
        if (! _self.last_valid_path)
            return;

        // For now assume we are on Windows and that path is not a UNC path
        let bits = _self.last_valid_path.split('/');
        if (bits.length < 2)
            return; // this means that there is no parent dir to go up to!

        let up_one_dir_path = bits.slice(0, -1).join('/');
        _self.set_path_value(up_one_dir_path);
        _self.validate_dirpath(up_one_dir_path, "pwba.${P}.apply_path_input_validation");
    }

    _self.select_folder_item = function(li_el)
    {
        let folder_path = _self.last_valid_path + '/' + li_el._original_foldername;
        _self.set_path_value(folder_path);
        _self.validate_dirpath(folder_path, "pwba.${P}.apply_path_input_validation");
    };

    _self.select_file_item = function(li_el)
    {
        alert('File name: ' + li_el._original_filename);
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
            path_edit_el.blur();
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
