odoo.define('agenda-program', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    var toastr = require('website_utilities.notifications').toastr;

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

    $(function() {
        function showProgramPathInfo () {
            // Info box (guidance)
            if(!$('#track-my-program-path').length || $('#track-my-program-path').is(":hidden")){

                toastr.options = {
                  "closeButton": false,
                  "debug": false,
                  "newestOnTop": true,
                  "progressBar": true,
                  "positionClass": "toast-top-right",
                  "preventDuplicates": true,
                  "timeOut": "0",
                  "showEasing": "swing",
                  "hideEasing": "linear",
                  "showMethod": "fadeIn",
                  "hideMethod": "fadeOut"
                }

                var info_title = '<p>' + _t('Create your own program path') + '!</p>';
                var info_msg = '<p>' + _t('Login to create your own program path by selecting presentations from the program by pressing the star symbol') + ' <span class="fa fa-star-o" />.</p>';
                info_msg += '<p>' + _t('You can also share your program path with others.') + '</p>';
                info_msg += '<p>' + _t('Nb! creating a program path will not mandate a participation for the selected presentations and also will not reserve a seat for you') + '.</p>';

                toastr.info(info_msg, info_title);
            }
        }

        // Run with timeout to get translations working
        setTimeout(showProgramPathInfo, 500);
    });
});
