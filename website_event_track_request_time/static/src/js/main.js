odoo.define('website_event_track_request_time.event_track_application_type', function (require) {
    "use strict";

    var _t = require('web.core')._t;
    // var loadingScreen = require('website_utilities.loader').loadingScreen;

    $(function () {


        $("#type").on("change", function () {
            var workshop = $("#type option:selected").attr("data-workshop");
            if (workshop) {
                console.log("====POISTETAAN CLASS=====");
            } else {
                console.log("===LISATAAN CLASS====");
            }

        });
    });
});
