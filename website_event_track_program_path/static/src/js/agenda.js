odoo.define('agenda-program', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    $('div.event-track-program-path')
        .click(function() {
            // TODO: AJAX save
            var action = '/event/agenda/program/save';
            var active = $(this).find('.track-program-path-icon-enabled').is(":visible");
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

            // Set my path link as visible
            // TODO: don't show if path is empty
            if($('#track-my-program-path').is(':hidden')){
                $('#track-my-program-path').removeClass('hidden');
            }
        })

    $('.track-program-path-icon-nologin').click(function() {
        alert(_t('Please sign in before customizing your program'));
    });

    $('div.event-track-program-path')
        .mouseenter(function() {
            $(this).tooltip();
        })
});
