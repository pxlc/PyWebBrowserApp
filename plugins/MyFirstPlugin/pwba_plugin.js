
function ${P}() {
    let _self = this;
    _self.my_id = 'blah';

    _self.show_popup = function()
    {
        let popup_div = document.getElementById("${P}_popup");
        popup_div.style.display = "block";
    };

    _self.test_fn = function()
    {
        alert('Hello from ${P}');
    };

    _self.test_callback = function()
    {
        _self.plugin_to_python("test_plugin_callback", {"message": "This is a test!"});
    };
}

pwba.register_plugin_js(${P});
