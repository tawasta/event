odoo.define('agenda', function (require) {
    var _t = require('web.core')._t;

    $('#filter-track-tags').click(function(){
        $('#track-search-form').submit();
    });
});
