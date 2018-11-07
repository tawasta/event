odoo.define('website_event_registration_address.registration', function (require) {
    "use strict";

    var _t = require('web.core')._t;

    $(function() {


    });
    $(document).on('show.bs.modal', '#modal_attendees_registration', function() {
        $('select.country-select').select2({
            placeholder: _t("Select a country")
        });
    });
});
