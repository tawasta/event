odoo.define("website_event_waiting_list.website_event", function (require) {
    "use strict";
    var ajax = require("web.ajax");
    var core = require("web.core");

    var _t = core._t;
    var WebsiteEvent = require("website_event.website_event");
    // Catch registration form event, because of JS for attendee details

    var EventWaitingForm = WebsiteEvent.include({
        /**
         * @override
         * @param {Event} ev
         */
        on_click: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest("form");
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            if ($($button).attr("name") === "waiting_list_button") {
                post.waiting_list_button = "True";
            }
            $("#registration_form table").siblings(".alert").remove();
            $("#registration_form select").each(function () {
                post[$(this).attr("name")] = $(this).val();
            });
            var tickets_ordered = _.some(
                _.map(post, function (value) {
                    return parseInt(value, 10);
                })
            );
            if (!tickets_ordered) {
                $('<div class="alert alert-info"/>')
                    .text(_t("Please select at least one ticket."))
                    .insertAfter("#registration_form table");
                return new Promise(function () {
                    return undefined;
                });
            }
            $button.attr("disabled", true);
            return ajax
                .jsonRpc($form.attr("action"), "call", post)
                .then(function (modal) {
                    var $modal = $(modal);
                    $modal.modal({backdrop: "static", keyboard: false});
                    $modal.find(".modal-body > div").removeClass("container");
                    $modal.appendTo("body").modal();
                    $modal.on("click", ".js_goto_event", function () {
                        $modal.modal("hide");
                        $button.prop("disabled", false);
                    });
                    $modal.on("click", ".close", function () {
                        $button.prop("disabled", false);
                    });
                });
        },
    });
    return EventWaitingForm;
});
