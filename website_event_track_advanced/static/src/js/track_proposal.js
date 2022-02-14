odoo.define("website_event_track_advanced.track_proposal", function (require) {
    var ajax = require("web.ajax");
    var Widget = require("web.Widget");
    var publicWidget = require("web.public.widget");

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
