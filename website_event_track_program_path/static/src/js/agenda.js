odoo.define('agenda-program', function (require) {
    var _t = require('web.core')._t;

    $('div.event-track-program-path')
        .click(function() {
            // TODO: AJAX save

            $(this).find('.track-program-path-icon').toggle();
        })

    $('div.event-track-program-path')
        .mouseenter(function() {
            $(this).tooltip();
        })
});
