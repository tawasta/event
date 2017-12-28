odoo.define('track_view', function (require) {
    var _t = require('web.core')._t;

    // Allow collapsing panel items
    $( ".panel-heading" ).click(function() {
        $(this).next().slideToggle('800', function() {});
    });
});
