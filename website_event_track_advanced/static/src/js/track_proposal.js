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
                    // Validate attachment size
                    $("#attachment_ids").bind("change", function () {
                        if (!this.files[0]) {
                            return true;
                        }
                        var attachment_size = this.files[0].size;
                        var max_size = 30 * 1024 * 1024;
                        if (attachment_size > max_size) {
                            $("#attachment-label").text("");
                            $("#attachment-file").val("");
                            // Show the error div
                            $("#track-application-attachment-error-div").removeClass(
                                "hidden"
                            );
                        } else {
                            // Hide the error div
                            $("#track-application-attachment-error-div").addClass(
                                "hidden"
                            );
                        }
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
                    // Show reload confirmation if modal is open
                    window.onbeforeunload = function (e) {
                        if ($modal.hasClass("show")) {
                            e.preventDefault();
                            return _t(
                                "Unsaved changes will be lost if you leave the page, are you sure?"
                            );
                        }
                    };
                    // enable tooltips with no delay
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
