odoo.define(
    "event_notification_subscription.portal_my_details_fields",
    function (require) {
        var publicWidget = require("web.public.widget");
        var core = require("web.core");
        var _t = core._t;

        publicWidget.registry.PortalTagSelection = publicWidget.Widget.extend({
            selector: ".o_portal_details",
            events: {
                "change #tag": "_onTagChange",
            },

            /**
             * @override
             */
            start: function () {
                this.$tagSelect = this.$("#tag");
                this.$hiddenMode = this.$("#hiddenmode");

                // Alustetaan Select2
                this.$tagSelect.select2({
                    placeholder: _t("Select tags..."),
                    allowClear: true,
                });

                // Päivitetään piilotettu kenttä alkutilanteessa
                this._updateHiddenField();

                return this._super.apply(this, arguments);
            },

            /**
             * Päivittää piilotetun input-kentän valittujen kategorioiden perusteella.
             * @private
             */
            _updateHiddenField: function () {
                var selectedTags = this.$tagSelect.val() || [];
                this.$hiddenMode.val(selectedTags.toString());
            },

            /**
             * Käsittelee kategorian valinnan muutoksen.
             * @private
             */
            _onTagChange: function () {
                this._updateHiddenField();
            },
        });
    }
);
