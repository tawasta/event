odoo.define("website_event_events_snippet.s_events_list_frontend", function (require) {
    "use strict";

    var core = require("web.core");
    var wUtils = require("website.utils");
    var publicWidget = require("web.public.widget");

    var _t = core._t;

    publicWidget.registry.js_get_events = publicWidget.Widget.extend({
        selector: ".js_get_events",
        disabledInEditableMode: false,

        /**
         * @override
         */
        start: function () {
            var self = this;
            const data = self.$target[0].dataset;
            const promoted = data.promoted === "true" || false;
            const limit = parseInt(data.eventsLimit, 10) || 3;
            const category = data.category_selection || 0;
            let eventType = data.eventType;
            if (eventType === undefined) {
                eventType = "upcoming";
            }

            // Compatibility with old template xml id
            if (
                data.template &&
                data.template.endsWith(".s_events_list_card_template")
            ) {
                data.template =
                    "website_event_events_snippet.s_events_list_card_template";
            }
            const template =
                data.template ||
                "website_event_events_snippet.s_events_list_card_template";
            const loading = data.loading === "true";
            const order = data.order || "date_begin asc";

            this.$target.empty();
            this.$target.attr("contenteditable", "False");

            var domain = [];
            if (promoted) {
                domain.push(["is_promoted", "=", true]);
            }

            var prom = new Promise(function (resolve) {
                self._rpc({
                    route: "/event/render_events_list",
                    params: {
                        template: template,
                        domain: domain,
                        limit: limit,
                        order: order,
                        eventType: eventType,
                        category: category,
                    },
                })
                    .then(function (events) {
                        var $events = $(events).filter(".s_events_list_event");
                        if (!$events.length) {
                            self.$target.append(
                                $("<div/>", {class: "col-md-6 offset-md-3"}).append(
                                    $("<div/>", {
                                        class: "alert alert-warning alert-dismissible text-center",
                                        text: _t(
                                            "No event was found. Make sure your events are published."
                                        ),
                                    })
                                )
                            );
                            resolve();
                        }

                        if (loading) {
                            // Perform an intro animation
                            self._showLoading($events);
                        } else {
                            self.$target.html($events);
                        }

                        // If the body contains editor_enable class, the user
                        // is in edit mode.
                        var inEditMode = $("body").hasClass("editor_enable");

                        // If in edit mode, place an element over the event banner to
                        // prevent colorPickerWidget is null error caused by
                        // clicking the image and then editing the filter values.
                        if (inEditMode) {
                            self.$target
                                .find(".s_events_list_event_cover")
                                .each(function () {
                                    var $cover = $(this);
                                    var $overlay = $(
                                        '<div class="cover-overlay"></div>'
                                    );
                                    $cover.after($overlay);
                                });
                        }

                        resolve();
                    })
                    .guardedCatch(function () {
                        if (self.editableMode) {
                            self.$target.append(
                                $("<p/>", {
                                    class: "text-danger",
                                    text: _t(
                                        "An error occured with this events list block. If the problem persists, please consider deleting it and adding a new one"
                                    ),
                                })
                            );
                        }
                        resolve();
                    });
            });
            return Promise.all([this._super.apply(this, arguments), prom]);
        },
        /**
         * @override
         */
        destroy: function () {
            this.$target.empty();
            this._super.apply(this, arguments);
        },

        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * @private
         * @param {Object} $events
         */
        _showLoading: function ($events) {
            var self = this;

            _.each($events, function (eventi, i) {
                var $eventi = $(eventi);
                var $progress = $eventi.find(".s_events_list_loader");
                var bgUrl =
                    $eventi
                        .find(".o_record_cover_image")
                        .css("background-image")
                        .replace("url(", "")
                        .replace(")", "")
                        .replace(/"/gi, "") || "none";

                // Append $event to the snippet, regardless by the loading state.
                $eventi.appendTo(self.$target);

                // No cover-image found. Add a 'flag' class and exit.
                if (bgUrl === "none") {
                    $eventi.addClass("s_events_list_loader_no_cover");
                    $progress.remove();
                    return;
                }

                // Cover image found. Show the spinning icon.
                $progress
                    .find("> div")
                    .removeClass("d-none")
                    .css("animation-delay", i * 200 + "ms");
                var $dummyImg = $("<img/>", {src: bgUrl});

                // If the image is not loaded in 10 sec, remove loader and provide a fallback bg-color to the container.
                // Hopefully one day the image will load, covering the bg-color...
                var timer = setTimeout(function () {
                    $eventi.find(".o_record_cover_image").addClass("bg-200");
                    $progress.remove();
                }, 10000);

                wUtils.onceAllImagesLoaded($dummyImg).then(function () {
                    $progress.fadeOut(500, function () {
                        $progress.removeClass("d-flex");
                    });

                    $dummyImg.remove();
                    clearTimeout(timer);
                });
            });
        },
    });
});
