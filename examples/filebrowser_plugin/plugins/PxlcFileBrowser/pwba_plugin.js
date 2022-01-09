
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
    }

    _self.hide = function()
    {
        if (! _self.outer_div) {
            _self.outer_div = document.getElementById("id_${P}_outer");
        }
        _self.outer_div.style.display = "none";
    }
}

//
// NOTE: Here is how you get a callback setup to run once the document is ready (and all DOM elements are available)
//
document.addEventListener('DOMContentLoaded', (event) => {
    //the event occurred
    console.log(':: EXECUTING onload callback for ENTER key.');
    document.getElementById("id_${P}_pathEdit").onkeyup = function(e) {
        if (e.key === 'Enter' || e.code === 13) {
            console.log(':: Got ENTER key!'); // TODO: validate path entered here
        }
    };
});

pwba.register_plugin_js(${P});
