/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.InviteOthersWidget = publicWidget.Widget.extend({
    selector: '#modal_ticket_registration',

    events: {
        'change #invite_others_switch': '_onInviteOthersSwitchChange',
    },

    start: function () {
        this._super.apply(this, arguments);
        console.log("InviteOthersWidget started");

        this.coreTicketOptions = {};
        this._saveCoreTicketOptions();
        this._updateTicketOptions();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Tallentaa core-selectin alkuperäiset valinnat, jotta ne voidaan palauttaa myöhemmin
     * @private
     */
    _saveCoreTicketOptions: function () {
        const self = this;
        this.$("select[name^='nb_register-']").each(function () {
            const selectName = $(this).attr('name');
            self.coreTicketOptions[selectName] = $(this).html();
        });
    },

    /**
     * Käsittelee liukukytkimen muutoksen
     * @private
     */
    _onInviteOthersSwitchChange: function () {
        this._updateTicketOptions();
    },

    /**
     * Päivittää lippuvalintakentän näkyvyyden ja valinnat riippuen liukukytkimen tilasta
     * @private
     */
    _updateTicketOptions: function () {
        const inviteOthersChecked = this.$('#invite_others_switch').is(':checked');

        if (inviteOthersChecked) {
            this._restoreCoreTicketOptions('other_nb_register-');
        } else {
            this._setSingleTicketOptions('nb_register-');
        }
    },

    /**
     * Palauttaa core-vaihtoehdot select-kenttiin ja päivittää name-arvon
     * @private
     * @param {string} namePrefix - nimi-prefix, joko "nb_register-" tai "other_nb_register-"
     */
    _restoreCoreTicketOptions: function (namePrefix) {
        const self = this;
        this.$("select[name^='nb_register-'], select[name^='other_nb_register-']").each(function () {
            const ticketId = $(this).attr('name').split('-')[1];
            $(this).html(self.coreTicketOptions['nb_register-' + ticketId]);
            $(this).attr('name', namePrefix + ticketId);
        });
    },

    /**
     * Asettaa 0 ja 1 vaihtoehdot select-kenttiin ja päivittää name-arvon
     * @private
     * @param {string} namePrefix - nimi-prefix, joko "nb_register-" tai "other_nb_register-"
     */
    _setSingleTicketOptions: function (namePrefix) {
        this.$("select[name^='nb_register-'], select[name^='other_nb_register-']").each(function () {
            const ticketId = $(this).attr('name').split('-')[1];
            $(this).empty();
            $(this).append(new Option(0, 0));
            $(this).append(new Option(1, 1));
            $(this).val(1);
            $(this).attr('name', namePrefix + ticketId);
        });
    },
});

export default publicWidget.registry.InviteOthersWidget;
