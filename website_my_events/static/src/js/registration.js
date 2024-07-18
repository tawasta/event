/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {jsonrpc} from "@web/core/network/rpc_service";

publicWidget.registry.PortalMyEvents = publicWidget.Widget.extend({
    selector: ".portal_my_events",

    /**
     * @override
     */
    start: function () {
        var self = this;

        $("#cancelModal").on("show.bs.modal", function (e) {
            var removeRegistration = $(e.relatedTarget).data("registration-id");
            $(e.currentTarget)
                .find('input[name="cancel_registration_id"]')
                .val(removeRegistration);
        });

        $(document).on("click", ".delete-confirm", function () {
            var registrationValue = document.getElementsByName(
                "cancel_registration_id"
            )[0].value;
            var action = "/registration/cancel/" + registrationValue;
            $("#cancelModal").modal("hide");
            jsonrpc(action, "call", {}).then(function () {
                location.reload();
            });
        });

        return this._super.apply(this, arguments);
    },
});

export default publicWidget.registry.PortalMyEvents;
