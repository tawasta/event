odoo.define('website_event_registration_profession.registration', function (require) {
    "use strict";

    var _t = require('web.core')._t;

    $(function() {

        $('.profession-select').select2({
            placeholder: _t("Select a profession")
        });
    });
});
