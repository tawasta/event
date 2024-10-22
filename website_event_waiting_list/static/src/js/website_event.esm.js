/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {jsonrpc} from "@web/core/network/rpc_service";

// Ensimmäinen tarkistetaan ja varmennetaan, että EventRegistrationFormInstance on määritelty oikein
const EventRegistrationFormInstance =
    publicWidget.registry.EventRegistrationFormInstance;

if (EventRegistrationFormInstance) {
    EventRegistrationFormInstance.include({
        /**
         * @override
         */
        start: function () {
            var self = this;
            const post = this._getPost();
            const noTicketsOrdered = Object.values(post)
                .map((value) => parseInt(value))
                .every((value) => value === 0);
            var res = this._super.apply(this, arguments).then(function () {
                $("#registration_form .a-submit")
                    .off("click")
                    .click(function (ev) {
                        self.on_click(ev);
                    })
                    .prop("disabled", noTicketsOrdered);

                // Poista disabled attribuutti waiting_list_buttonista
                const $waitingListButton = $(
                    '#registration_form button[name="waiting_list_button"]'
                );
                if ($waitingListButton.length) {
                    $waitingListButton.removeAttr("disabled");
                }
            });
            return res;
        },

        _getPost: function () {
            var post = {};
            $("#registration_form select").each(function () {
                post[$(this).attr("name")] = $(this).val();
            });
            const waitingListValue = $(
                '#registration_form input[name="waiting_list_registration"]'
            ).val();
            if (waitingListValue) {
                post.waiting_list_registration = waitingListValue;
            }
            console.log("===POST===");
            console.log(post);
            return post;
        },

        /**
         * @private
         * @param {Event} ev
         */
        on_click: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest("form");
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            console.log("====ON CLICK====");
            const post = this._getPost();
            console.log(post);
            $button.attr("disabled", true);
            return jsonrpc($form.attr("action"), post).then(function (modal) {
                if (modal.redirect) {
                    window.location.href = modal.redirect; // Ohjaa käyttäjä uudelle sivulle
                } else {
                    var $modal = $(modal);
                    $modal.find(".modal-body > div").removeClass("container"); // Retrocompatibility - REMOVE ME in master / saas-19
                    $modal.appendTo(document.body);
                    // TimoK: This has been commented out so that eslint won't throw an error
                    // const modalBS = new Modal($modal[0], {
                    //    backdrop: "static",
                    //    keyboard: false,
                    // });
                    // modalBS.show();
                    $modal.appendTo("body").modal("show");
                    $modal.on("click", ".js_goto_event", function () {
                        $modal.modal("hide");
                        $button.prop("disabled", false);
                    });
                    $modal.on("click", ".btn-close", function () {
                        $button.prop("disabled", false);
                    });
                }
            });
        },
    });
}

export default EventRegistrationFormInstance;
