odoo.define("website_event_track_advanced.track_proposal", function (require) {
    var ajax = require("web.ajax");
    var core = require("web.core");
    var Widget = require("web.Widget");
    var publicWidget = require("web.public.widget");
    var _t = core._t;

    // Catch registration form event, because of JS for attendee details
    var TrackProposalForm = Widget.extend({
        /**
         * @override
         */
        start: function () {
            var self = this;
            var res = this._super.apply(this.arguments).then(function () {
                $("#track_proposal .a-submit")
                    .off("click")
                    .click(function (ev) {
                        self.on_click(ev);
                    });
            });
            return res;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        /**
         * @private
         * @param {Event} ev
         */
        on_click: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest("form");
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            post.track_id = $button[0].id;
            $button.attr("disabled", true);
            function toggleDisabled(target) {
                var toggle_target = $(target).data("toggle");
                if (toggle_target) {
                    var obj = $("#" + toggle_target);
                    if (target.checked) {
                        obj.removeAttr("disabled");
                    } else {
                        obj.attr("disabled", "disabled");
                    }
                }
            }
            return ajax
                .jsonRpc($form.attr("action"), "call", post)
                .then(function (modal) {
                    var submitted = false;
                    var $modal = $(modal);
                    $modal.modal({backdrop: "static", keyboard: false});
                    $modal.find(".modal-body > div").removeClass("container");
                    $modal.appendTo("body").modal();
                    $modal.on("click", ".js_goto_event", function () {
                        $modal.modal("hide");
                        $button.prop("disabled", false);
                    });
                    // Remove attachment with button
                    $("#btn-remove-attachment").click(function () {
                        $("#attachment_ids").val("");
                    });
                    // Toggle disabled with checkbox
                    $("input:checkbox")
                        .each(function () {
                            toggleDisabled(this);
                        })
                        .on("input", function () {
                            toggleDisabled(this);
                        });
                    // Show warning on modal close
                    $modal.on("click", ".closefirstmodal", function () {
                        $button.prop("disabled", false);
                        $("#modal_event_track_warning").modal("show");
                    });
                    // Hide both modals on warning confirm
                    $modal.on("click", ".confirmclosed", function () {
                        $button.prop("disabled", false);
                        $("#modal_event_track_warning").modal("hide");
                        $("#modal_event_track_application").modal("hide");
                    });
                    // Hide warning modal on warning cancel
                    $modal.on("click", ".cancelclosed", function () {
                        $button.prop("disabled", false);
                        $("#modal_event_track_warning").modal("hide");
                    });
                    // Remove proposal form modal once it's hidden
                    $modal.on("hidden.bs.modal", function (e) {
                        // Fixes scrolling if another modal remains open
                        if ($(".modal.show").length > 0) {
                            $("body").addClass("modal-open");
                        }
                        if (this === e.target) {
                            this.remove();
                        }
                    });
                    // Add speaker (contact) row(s)
                    $("#add_speaker").click(function () {
                        var speaker_count =
                            Number($("#track-application-speaker-input-index").val()) +
                            1;
                        $("#track-application-speaker-input-index").val(speaker_count);
                        console.log($("#track-application-speaker-input-index").val());
                        // Clone the last row
                        var row = $(
                            ".track-application-speakers-div-row-container:last"
                        )
                            .clone()
                            .appendTo(".track-application-speakers-div-container");
                        row.removeAttr("id");
                        row.find("button").removeAttr("disabled");
                        // Clear the values
                        row.find("input").val("");
                        // Add a unique id for div
                        row.prop("id", speaker_count);
                        // Add a unique name
                        row.find("input").each(function () {
                            var property_value = $(this).prop("name");
                            var index_name =
                                property_value.substring(0, property_value.length - 3) +
                                "[" +
                                speaker_count +
                                "]";
                            $(this).prop("name", index_name);
                        });
                        // Add a unique label
                        row.find("label").each(function () {
                            var property_value = $(this).prop("for");
                            var index_name =
                                property_value.substring(0, property_value.length - 3) +
                                "[" +
                                speaker_count +
                                "]";
                            $(this).prop("for", index_name);
                        });
                        // Add a unique span text
                        row.find(".presenter-span").text("Presenter #" + speaker_count);
                    });

                    // Remove speaker rows
                    $(document).on("click", ".btn-remove-speaker", function () {
                        var confirm_message = _t(
                            "Are you sure you want to delete this speaker?"
                        );

                        if (window.confirm(confirm_message)) {
                            $(this).parent().remove();
                            var speaker_count =
                                Number(
                                    $("#track-application-speaker-input-index").val()
                                ) - 1;
                            $("#track-application-speaker-input-index").val(
                                speaker_count
                            );
                        }
                    });

                    // Show reload confirmation if modal is open
                    window.onbeforeunload = function (e) {
                        if ($modal.hasClass("show") && !submitted) {
                            e.preventDefault();
                            return _t(
                                "Unsaved changes will be lost if you leave the page, are you sure?"
                            );
                        }
                    };
                    $("#type").change(function () {
                        $("#application_type_description").text(
                            $("#type option:selected").attr("data-description") || ""
                        );
                        var workshop = $("#type option:selected").attr("data-workshop");
                        console.log(workshop);
                        if (!workshop) {
                            $("#track-application-workshop-div").addClass("d-none");
                            $("#track-application-workshop-div")
                                .find("input[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", true);
                                });
                            $("#track-application-workshop-div")
                                .find("select[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", true);
                                });
                            $("#track-application-workshop-div")
                                .find("textarea[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", true);
                                });
                        } else {
                            $("#track-application-workshop-div").removeClass("d-none");
                            $("#track-application-workshop-div")
                                .find("input[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", true);
                                });
                            $("#track-application-workshop-div")
                                .find("select[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", true);
                                });
                            $("#track-application-workshop-div")
                                .find("textarea[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", true);
                                });
                        }
                    });

                    // Enable tooltips with no delay
                    $(document).ready(function () {
                        $("body").tooltip({
                            selector: "[data-toggle=tooltip]",
                            delay: {show: 0, hide: 0},
                        });
                    });
                    $modal.on("click", ".application-submit", function (event) {
                        var form = document.getElementById("track-application-form");
                        if (form.checkValidity() === false) {
                            event.preventDefault();
                            event.stopPropagation();
                        } else {
                            submitted = true;
                        }
                        form.classList.add("was-validated");
                    });
                });
        },
    });

    publicWidget.registry.TrackProposalFormInstance = publicWidget.Widget.extend({
        selector: "#track_proposal",

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            this.instance = new TrackProposalForm(this);
            return Promise.all([def, this.instance.attachTo(this.$el)]);
        },
        /**
         * @override
         */
        destroy: function () {
            console.log("destroy");
            this.instance.setElement(null);
            this._super.apply(this, arguments);
            this.instance.setElement(this.$el);
        },
    });

    return TrackProposalForm;
});
