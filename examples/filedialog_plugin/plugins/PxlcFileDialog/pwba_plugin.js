
function ${P}() {
    let _self = this;

    _self.outer_div = null;

    _self.init = function()  // this is custom initialization for the specific plugin
    {
        document.getElementById("id_${P}_pathEdit").onkeyup = function(e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                console.log(':: Got ENTER key!'); // TODO: validate path entered here
            }
        };
    };

    _self.show = function()
    {
        if (! _self.outer_div) {
            _self.outer_div = document.getElementById("id_${P}_outer");
        }
        _self.outer_div.style.display = "block";
    }

    _self.hide = function()
    {
        if (! _self.outer_div) {
            _self.outer_div = document.getElementById("id_${P}_outer");
        }
        _self.outer_div.style.display = "none";
    }


    /*
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

    _self.roundtrip_to_python = function()
    {
        _self.plugin_to_python("roundtrip_from_js",
                               {"alert_msg": "Alert message passed through from JS to Python and back to JS!"});
    };

    _self.roundtrip_from_python = function(op_data)
    {
        alert(op_data.alert_msg);
    };
    */
}

pwba.register_plugin_js(${P});
