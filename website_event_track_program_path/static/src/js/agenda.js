odoo.define('agenda-program', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    $('div.event-track-program-path')
        .click(function() {
            // TODO: AJAX save
            var action = '/event/agenda/program/save';
            var active = $('#track-program-path-icon-enabled').is(":visible");
            var cell = $(this).closest('td');

            var values = {
                'active': active,
                'track_id': cell.attr('name'),
            };

            ajax.jsonRpc(action, 'call', values).then(function(data){
                if(data == 200){
                    // Success. Nothing to do here
                }
                else if(data == 500){
                    // Error while handling the request
                    alert(_t('Error while trying to save. Please reload the page!'));
                }
            });

            $(this).find('.track-program-path-icon').toggle();
        })

    $('div.event-track-program-path')
        .mouseenter(function() {
            $(this).tooltip();
        })
});
