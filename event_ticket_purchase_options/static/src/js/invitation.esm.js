/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import Dialog from "@web/legacy/js/core/dialog";
import {_t} from "@web/core/l10n/translation";

publicWidget.registry.PortalInvite = publicWidget.Widget.extend({
    selector: ".portal_my_events",

    /**
     * @override
     */
    start: function () {
        this._bindModalEvents();
        this._bindFormSubmit();
        return this._super.apply(this, arguments);
    },

    _bindModalEvents: function () {
        $("#inviteModal").on("show.bs.modal", function (e) {
            var registration = $(e.relatedTarget).data("registration-id");
            $("#registration_id_modal").val(registration);
        });
    },

    _bindFormSubmit: function () {
        const self = this;

        $("#invite-form").on("submit", function (e) {
            e.preventDefault(); // Estä oletuslähetys

            // Lomakkeen validointi (HTML5:n reportValidity-metodi)
            if (!this.reportValidity()) {
                return;
            }

            self._showLoadingScreen("Lähetetään kutsua, odota hetki...");

            // Kerää lomaketiedot
            const formData = new FormData(this);
            const action = $(this).attr("action");

            // Lähetä lomake AJAXilla
            $.ajax({
                url: action,
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    const jsonResponse = JSON.parse(response);
                    if (jsonResponse.status === "success") {
                        $("#invite-form")[0].reset();
                        $("#inviteModal").modal("hide");

                        self._showSuccessMessage(jsonResponse.message);
                    } else if (jsonResponse.error) {
                        console.error("Virhe: " + jsonResponse.error);
                    }
                },
                error: function () {
                    console.error("Tapahtui virhe lähetyksessä.");
                    alert("Odottamaton virhe.");
                },
                complete: function () {
                    self._hideLoadingScreen();
                },
            });
        });
    },

    /**
     * Näyttää latausruudun viestillä.
     */
    _showLoadingScreen: function (message) {
        const displayMessage = `
            <div id="loading-screen" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                text-align: center;
                font-size: 20px;
            ">
                <div>
                    <img src="/web/static/img/spin.png"
                        style="animation: fa-spin 1s infinite steps(12); width: 50px; height: 50px;"/>
                    <br/><br/>
                    <h4>${message}</h4>
                </div>
            </div>`;
        $("body").append(displayMessage);
    },

    _hideLoadingScreen: function () {
        $("#loading-screen").remove();
    },

    /**
     * Näyttää onnistumisviestin.
     */
    _showSuccessMessage: function (message) {
        new Dialog(this, {
            title: _t("Success"),
            size: "medium",
            $content: $("<div/>").html(message),
            buttons: [
                {
                    text: _t("OK"),
                    close: true,
                    click: function () {
                        location.reload();
                    },
                },
            ],
        }).open();
    },
});

export default publicWidget.registry.PortalInvite;
