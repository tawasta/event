/* eslint-disable */
odoo.define("event_recaptcha.event", function (require) {
    "use strict";

    var SomeWidgetName = require("website_event.website_event"); // Korvaa oikealla module ja widget nimellä
    var ajax = require("web.ajax");

    SomeWidgetName.include({
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
            ajax.jsonRpc($form.attr("action"), "call", post).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: "static", keyboard: false});
                $modal.find(".modal-body > div").removeClass("container");
                $modal.appendTo("body").modal();
                // Init fields
                $modal.on("click", ".btn-primary", function (event) {
                    var $attendee_form = $modal.find("#attendee_registration").first();
                    var submit_values = self._submitForm($attendee_form, $modal);
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
        _submitForm: function ($form, $modal) {
            var recaptcha = $("#g-recaptcha-response").val();
            var error = false;
            $("#err").text("");
            $("#error-message").text("");

            if (recaptcha === "") {
                console.log("===CATPCHA KUNTOON=====");
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
