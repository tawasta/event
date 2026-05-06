/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SingleTicketPurchaseLimit = publicWidget.Widget.extend({
    selector: "#registration_form",

    events: {
        "change select[name^='nb_register-']": "_onTicketQuantityChange",
    },

    /**
     * @override
     */
    start: function () {
        const res = this._super.apply(this, arguments);

        this._limitTicketSelectOptions();
        this._enforceSingleTicketSelection();
        this._toggleSubmitButton();

        return res;
    },

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    /**
     * Restrict each ticket select to values 0 or 1.
     */
    _limitTicketSelectOptions: function () {
        this.$("select[name^='nb_register-']").each(function () {
            const currentValue = parseInt(this.value || "0");

            $(this)
                .find("option")
                .each(function () {
                    if (parseInt(this.value || "0") > 1) {
                        $(this).remove();
                    }
                });

            this.value = currentValue > 0 ? "1" : "0";
        });
    },

    /**
     * Ensure that only one ticket can be selected in total.
     *
     * If a new ticket is selected, all others are reset to 0.
     */
    _enforceSingleTicketSelection: function (changedSelect) {
        if (changedSelect && parseInt(changedSelect.value || "0") > 0) {
            this.$("select[name^='nb_register-']").each(function () {
                if (this !== changedSelect) {
                    this.value = "0";
                }
            });
            return;
        }

        let found = false;

        this.$("select[name^='nb_register-']").each(function () {
            if (parseInt(this.value || "0") > 0) {
                if (found) {
                    this.value = "0";
                } else {
                    this.value = "1";
                    found = true;
                }
            }
        });
    },

    /**
     * Enable submit only when exactly one ticket is selected
     */
    _toggleSubmitButton: function () {
        const total = this.$("select[name^='nb_register-']")
            .toArray()
            .reduce((sum, el) => sum + parseInt(el.value || "0"), 0);

        this.$("button[type='submit']").prop("disabled", total !== 1);
    },

    // --------------------------------------------------------------------------
    // Handlers
    // --------------------------------------------------------------------------

    _onTicketQuantityChange: function (ev) {
        this._limitTicketSelectOptions();
        this._enforceSingleTicketSelection(ev.currentTarget);
        this._toggleSubmitButton();
    },
});

export default publicWidget.registry.SingleTicketPurchaseLimit;
