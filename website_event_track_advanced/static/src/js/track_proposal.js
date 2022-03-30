odoo.define("website_event_track_advanced.track_proposal", function (require) {
    var ajax = require("web.ajax");
    var core = require("web.core");
    var Widget = require("web.Widget");
    var publicWidget = require("web.public.widget");
    var _t = core._t;
    var weDefaultOptions = require("web_editor.wysiwyg.default_options");
    var wysiwygLoader = require("web_editor.loader");

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
            var self = this;
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
                        obj.siblings()
                            .find(".note-editable")
                            .attr("contenteditable", "true");
                    } else {
                        obj.attr("disabled", "disabled");
                        obj.siblings()
                            .find(".note-editable")
                            .attr("contenteditable", "false");
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

                    $(".tags-select").select2({
                        maximumSelectionSize: 3,
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

                    // Show warning on modal close if editable
                    $modal.on("click", ".warning-close-modal", function () {
                        if ($("input#editable").val()) {
                            $("#modal_event_track_warning_close_modal").modal("show");
                        } else {
                            $button.prop("disabled", false);
                            $("#modal_event_track_application").modal("hide");
                        }
                    });

                    // Hide both modals on warning confirm
                    $modal.on(
                        "click",
                        ".warning-confirm-modal_event_track_warning_close_modal",
                        function () {
                            $button.prop("disabled", false);
                            $("#modal_event_track_warning_close_modal").modal("hide");
                            $("#modal_event_track_application").modal("hide");
                        }
                    );

                    // Hide warning modal on warning cancel
                    $modal.on(
                        "click",
                        ".warning-cancel-modal_event_track_warning_close_modal",
                        function () {
                            $("#modal_event_track_warning_close_modal").modal("hide");
                        }
                    );

                    // Show remove speaker warning modal
                    $modal.on("click", ".btn-remove-speaker", function () {
                        $("#modal_event_track_warning_remove_presenter").modal("show");
                        $("#modal_event_track_warning_remove_presenter").val(
                            $(this).parent()
                        );
                    });
                    // Hide warning modal and remove presenter on warning confirm
                    $modal.on(
                        "click",
                        ".warning-confirm-modal_event_track_warning_remove_presenter",
                        function () {
                            $("#modal_event_track_warning_remove_presenter").modal(
                                "hide"
                            );
                            var presenter = $(
                                "#modal_event_track_warning_remove_presenter"
                            ).val();
                            presenter.remove();
                            var speaker_count =
                                Number(
                                    $("#track-application-speaker-input-index").val()
                                ) - 1;
                            $("#track-application-speaker-input-index").val(
                                speaker_count
                            );
                        }
                    );
                    // Hide warning modal on warning cancel
                    $modal.on(
                        "click",
                        ".warning-cancel-modal_event_track_warning_remove_presenter",
                        function () {
                            $("#modal_event_track_warning_remove_presenter").modal(
                                "hide"
                            );
                        }
                    );

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

                    // Validate file size
                    $("#attachment_ids").bind("change", function () {
                        if (!this.files[0]) {
                            return true;
                        }
                        var attachment_size = this.files[0].size;
                        var max_size = 30 * 1024 * 1024;
                        if (attachment_size > max_size) {
                            $("#attachment_ids").text("");
                            $("#attachment_ids").val("");
                        }
                    });

                    // Add speaker (contact) row(s)
                    $("#add_speaker").click(function () {
                        var speaker_count =
                            Number($("#track-application-speaker-input-index").val()) +
                            1;
                        $("#track-application-speaker-input-index").val(speaker_count);
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

                    // Show reload confirmation if modal is open and not submitted
                    window.onbeforeunload = function (e) {
                        if (
                            $modal.hasClass("show") &&
                            !submitted &&
                            $("input#editable").val()
                        ) {
                            e.preventDefault();
                            return _t(
                                "Unsaved changes will be lost if you leave the page, are you sure?"
                            );
                        }
                    };

                    // Display workshop questions depending on type
                    $("#type").change(function () {
                        $("#application_type_description").text(
                            $("#type option:selected").attr("data-description") || ""
                        );
                        var workshop = $("#type option:selected").attr("data-workshop");
                        // Enable workshop inputs
                        if (workshop) {
                            $("#track-application-workshop-div").removeClass("d-none");
                            $("#track-application-workshop-div")
                                .find("input#is_workshop")
                                .each(function () {
                                    $(this).attr("value", "true");
                                });
                            $("#track-application-workshop-div")
                                .find("input[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("input[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-div")
                                .find("select[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("select[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                });
                            $("#track-application-workshop-div")
                                .find("textarea[disabled]")
                                .each(function () {
                                    $(this).removeAttr("disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            $("#track-application-workshop-div")
                                .find("textarea[required-disabled]")
                                .each(function () {
                                    $(this).removeAttr("required-disabled");
                                    $(this).attr("required", "required");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "true");
                                });
                            // Disable workshop inputs
                        } else {
                            $("#track-application-workshop-div").addClass("d-none");
                            $("#track-application-workshop-div")
                                .find("input#is_workshop")
                                .each(function () {
                                    $(this).attr("value", "false");
                                });
                            $("#track-application-workshop-div")
                                .find("input")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("input[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("select")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("select[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                });
                            $("#track-application-workshop-div")
                                .find("textarea")
                                .each(function () {
                                    $(this).attr("disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                            $("#track-application-workshop-div")
                                .find("textarea[required]")
                                .each(function () {
                                    $(this).removeAttr("required");
                                    $(this).attr("required-disabled", "disabled");
                                    $(this)
                                        .siblings()
                                        .find(".note-editable")
                                        .attr("contenteditable", "false");
                                });
                        }
                    });

                    // Enable wysiwyg editor for textareas
                    $("#track-application-form")
                        .find("textarea.o_wysiwyg_loader")
                        .each(function () {
                            var $textarea = $(this);
                            var $textareaForm = $textarea.closest("form");
                            // Warning: Do not activate any option that adds inline style.
                            // Because the style is deleted after save.
                            var toolbar = [
                                ["style", ["style"]],
                                ["font", ["bold", "italic", "underline", "clear"]],
                                ["para", ["ul", "ol", "paragraph"]],
                                ["table", ["table"]],
                            ];
                            toolbar.push(["history", ["undo", "redo"]]);

                            var options = {
                                height: 200,
                                minHeight: 80,
                                toolbar: toolbar,
                                styleWithSpan: false,
                                styleTags: _.without(
                                    weDefaultOptions.styleTags,
                                    "h1",
                                    "h2",
                                    "h3"
                                ),
                                recordInfo: {
                                    res_model: "event.track",
                                },
                                disableFullMediaDialog: true,
                                disableResizeImage: true,
                            };
                            wysiwygLoader
                                .load(self, $textarea[0], options)
                                .then((wysiwyg) => {
                                    $textareaForm
                                        .find(".note-editable")
                                        .find("img.float-left")
                                        .removeClass("float-left");
                                    $textareaForm
                                        .find(".note-editable")
                                        .find("img.o_we_selected_image")
                                        .removeClass("o_we_selected_image");
                                    $textareaForm.on(
                                        "click",
                                        "button, .application-submit",
                                        () => {
                                            $textareaForm
                                                .find(".note-editable")
                                                .find("img.o_we_selected_image")
                                                .removeClass("o_we_selected_image");
                                            wysiwyg.save();
                                        }
                                    );
                                });
                        });

                    // Enable tooltips with no delay
                    $(document).ready(function () {
                        $("body").tooltip({
                            selector: "[data-toggle=tooltip]",
                            delay: {show: 0, hide: 0},
                        });
                    });

                    // Submit form and validate
                    $modal.on("click", ".application-submit", function (event) {
                        var form = document.getElementById("track-application-form");
                        if (form.checkValidity() === false) {
                            event.preventDefault();
                            event.stopPropagation();
                            var errorElements = document.querySelectorAll(
                                ".form-control:invalid, .form-check-input:invalid"
                            );
                            if (errorElements) {
                                var scrollLocation = $(errorElements[0]).offset().top;
                                var scrollInside = $modal.scrollTop();
                                $modal.animate(
                                    {
                                        scrollTop: scrollInside + scrollLocation,
                                    },
                                    500
                                );
                            }
                        } else {
                            submitted = true;
                            var input = document.createElement("input");
                            input.setAttribute("name", $(this).val());
                            input.setAttribute("value", $(this).val());
                            input.setAttribute("type", "hidden");
                            form.appendChild(input);
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
            this.instance.setElement(null);
            this._super.apply(this, arguments);
            this.instance.setElement(this.$el);
        },
    });

    return TrackProposalForm;
});
