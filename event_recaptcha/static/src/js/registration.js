/* eslint-disable */
odoo.define("event_recaptcha.event", function (require) {
    "use strict";

    var WebsiteEvent = require("website_event.website_event");
    var ajax = require("web.ajax");
    var core = require("web.core");

    var _t = core._t;

    WebsiteEvent.include({
        /**
         * @override
         */
        on_click: function (ev) {
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest("form");
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            if ($($button).attr("name") === "waiting_list_button") {
                post.waiting_list_button = "True";
            }
            $form.find("select").each(function () {
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
                    .insertAfter($form.find("table"));
                return new Promise(function () {});
            }
            $button.attr("disabled", true);
            ajax.jsonRpc($form.attr("action"), "call", post).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: "static", keyboard: false});
                $modal.find(".modal-body > div").removeClass("container");
                $modal.appendTo("body").modal();
                $modal.on("click", ".btn-primary", function (event) {
                    var $attendee_form = $modal.find("#attendee_registration").first();
                    var submit_values = self._submitForm($attendee_form, $modal, post);
                    if (jQuery.isEmptyObject(submit_values)) {
                        event.preventDefault();
                    } else {
                        post = Object.assign({}, post, submit_values);
                        var input = $("<input>")
                            .attr("type", "hidden")
                            .attr("name", "post-data")
                            .val(JSON.stringify(post));
                        $attendee_form.append($(input));
                    }
                });
            });
        },

        /**
         * Before submitting the answers, they are first validated and prepared for post.
         *
         * @param {Object} $form - contains the submitted form
         * @param {Object} $modal - contains the modal
         * @private
         * @returns {Dictionary} post - the dictionary to send in post
         */
        _submitForm: function ($form, $modal, post) {
            var recaptcha = $("#g-recaptcha-response").val();
            var error = false;
            $("#err").text("");
            $("#error-message").text("");

            if (recaptcha === "") {
                console.log("===CAPTCHA MISSING=====");
                var err_message = "Please check Captcha";
                $("#err").text(err_message);
                error = true;
            }
            if (!error) {
                return post;
            }
        },
    });
});
