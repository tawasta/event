odoo.define("event_recaptcha.event", function (require) {
    "use strict";

    var ajax = require("web.ajax");
    var WebsiteEvent = require("website_event.website_event");

    WebsiteEvent.include({
        on_click: function (ev) {
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest("form");
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            // Lisää waiting_list_button tila post objektiin, jos kyseessä on jonotuslistan nappi
            if ($button.attr("name") === "waiting_list_button") {
                post.waiting_list_button = "True";
            }
            $("#registration_form table").siblings(".alert").remove();
            $("#registration_form select").each(function () {
                post[$(this).attr("name")] = $(this).val();
            });
            var tickets_ordered = _.some(_.map(post, function (value) {
                return parseInt(value, 10);
            }));
            if (!tickets_ordered) {
                $('<div class="alert alert-info"/>')
                    .text(_t("Please select at least one ticket."))
                    .insertAfter("#registration_form table");
                return false;
            }

            var recaptcha = $("#g-recaptcha-response").val();
            if (recaptcha === "") {
                // Jos reCAPTCHA ei ole valittu, näytetään virheilmoitus eikä jatketa.
                alert("Please verify you are not a robot.");
                return false;
            } else {
                $button.attr("disabled", true);
                ajax.jsonRpc($form.attr("action"), "call", post).then(function (modal) {
                    var $modal = $(modal);
                    $modal.modal({backdrop: "static", keyboard: false});
                    $modal.find(".modal-body > div").removeClass("container");
                    $modal.appendTo("body").modal();
                    $modal.on("hidden.bs.modal", function () {
                        $button.prop("disabled", false);
                    });
                });
            }
        },
    });
});
