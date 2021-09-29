odoo.define('website_my_events.portal_my_events', function (require) {
    "use strict";

    var _t = require('web.core')._t;

    $(function() {

        $('#cancelModal').on('show.bs.modal', function(e) {
            var removeRegistration = $(e.relatedTarget).data('registration-id');
            $(e.currentTarget).find('input[name="cancel_registration_id"]').val(removeRegistration);
        });

        $(document).on('click', '.delete-confirm', function() {
            var registrationValue = document.getElementsByName('cancel_registration_id')[0].value;
            var action = '/registration/cancel/' + registrationValue;
            $('#cancelModal').modal('hide');
            $.get(action).done(function(data) {
                location.reload();
            });
        });
    });
});
