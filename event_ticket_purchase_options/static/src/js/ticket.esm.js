/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.InviteOthersWidget = publicWidget.Widget.extend({
    selector: "#modal_ticket_registration",

    events: {
        "change input[name='registration_option']": "_onRegistrationOptionChange",
    },

    /**
     * Modaalin avaamisen jälkeen suoritetaan koodi
     */
    start: function () {
        const res = this._super.apply(this, arguments);
        console.log("InviteOthersWidget started");

        // Käynnistetään widget vasta, kun modaalin sisältö on näkyvissä
        this.$el.closest(".modal").on("shown.bs.modal", () => {
            this.coreTicketOptions = {};
            this._saveCoreTicketOptions();
            this._updateTicketOptions();
            this._updateCardStyles();

            // Tarkista rekisteröintipainikkeen tila
            this._toggleRegisterButton();

            // Kuuntele lippujen määrän muutoksia, jotta painikkeen tila pysyy synkronoituna
            this.$el.on(
                "change",
                ".form-select",
                this._toggleRegisterButton.bind(this)
            );
        });

        return res;
    },

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    /**
     * Tallentaa core-selectin alkuperäiset valinnat, jotta ne voidaan palauttaa myöhemmin
     * @private
     */
    _saveCoreTicketOptions: function () {
        const self = this;
        this.$("select[name^='nb_register-']").each(function () {
            const selectName = $(this).attr("name");
            self.coreTicketOptions[selectName] = $(this).html();
        });
    },

    /**
     * Käsittelee radiopainikkeiden muutoksen
     * @private
     */
    _onRegistrationOptionChange: function () {
        this._updateTicketOptions();
        this._updateCardStyles();
        this._toggleRegisterButton();
    },

    /**
     * Päivittää lippuvalintakentän näkyvyyden ja valinnat riippuen valitusta vaihtoehdosta
     * @private
     */
    _updateTicketOptions: function () {
        const inviteOthersChecked = this.$("#register_others").is(":checked");

        if (inviteOthersChecked) {
            this._restoreCoreTicketOptions("other_nb_register-");
        } else {
            this._setSingleTicketOptions("nb_register-");
        }
    },

    /**
     * Palauttaa core-vaihtoehdot select-kenttiin ja päivittää name-arvon
     * @private
     * @param {String} namePrefix - nimi-prefix, joko "nb_register-" tai "other_nb_register-"
     */
    _restoreCoreTicketOptions: function (namePrefix) {
        const self = this;
        this.$("select[name^='nb_register-'], select[name^='other_nb_register-']").each(
            function () {
                const ticketId = $(this).attr("name").split("-")[1];
                $(this).html(self.coreTicketOptions["nb_register-" + ticketId]);
                $(this).attr("name", namePrefix + ticketId);
            }
        );
    },

    /**
     * Asettaa 0 ja 1 vaihtoehdot select-kenttiin ja päivittää name-arvon
     * @private
     * @param {String} namePrefix - nimi-prefix, joko "nb_register-" tai "other_nb_register-"
     */
    _setSingleTicketOptions: function (namePrefix) {
        this.$("select[name^='nb_register-'], select[name^='other_nb_register-']").each(
            function () {
                const ticketId = $(this).attr("name").split("-")[1];
                $(this).empty();
                $(this).append(new Option(0, 0));
                $(this).append(new Option(1, 1));
                $(this).val(1);
                $(this).attr("name", namePrefix + ticketId);
            }
        );
    },

    /**
     * Päivittää korttien tyylit, jotta valittu vaihtoehto näkyy aktiivisena
     * @private
     */
    _updateCardStyles: function () {
        // Poista aktiivinen tyyli kaikista korteista
        this.$(".card").removeClass("bg-success text-white shadow border-success");
        this.$(".card").addClass("border-secondary");

        // Lisää aktiivinen tyyli valittuun korttiin
        if (this.$("#register_self").is(":checked")) {
            this.$("#register_self")
                .closest(".card")
                .addClass("bg-success text-white shadow border-success")
                .removeClass("border-secondary");
        } else if (this.$("#register_others").is(":checked")) {
            this.$("#register_others")
                .closest(".card")
                .addClass("bg-success text-white shadow border-success")
                .removeClass("border-secondary");
        }
    },

    /**
     * Päivittää rekisteröintipainikkeen tilan riippuen siitä, onko valinta tehty ja lippuja valittu
     * @private
     */
    _toggleRegisterButton: function () {
        // Tarkista, onko jokin valinta tehty
        const isOptionSelected =
            this.$("input[name='registration_option']:checked").length > 0;

        // Tarkista, onko lippuja valittu (tässä viitataan core-widgetin logiikkaan)
        const isTicketSelected = this.$(".form-select")
            .toArray()
            .some((select) => parseInt(select.value) > 0);

        // Varmista, että rekisteröintipainike on aktiivinen vain, jos molemmat ehdot täyttyvät
        const isButtonEnabled = isOptionSelected && isTicketSelected;

        // Ota rekisteröintipainike käyttöön tai poista käytöstä riippuen molemmista ehdoista
        this.$("button[type='submit']").prop("disabled", !isButtonEnabled);
    },
});

export default publicWidget.registry.InviteOthersWidget;
