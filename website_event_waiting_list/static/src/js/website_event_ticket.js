/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ticketDetailsWidget.include({
    start: function () {
        this._super.apply(this, arguments);
        // Aktivoi painike, jos jonotuslista on käytössä
        console.log("=======TAAALLA=====");
        const $waitingListButton = this.$('button[name="waiting_list_button"]');
        console.log("Button found:", $waitingListButton.length);
        if ($waitingListButton.length) {
            console.log("0000 - Removing disabled attribute");
            $waitingListButton.removeAttr('disabled');
            console.log("Button after removing disabled:", $waitingListButton);
        }
    },
    
    _onTicketQuantityChange: function () {
        this._super.apply(this, arguments);
        console.log("=======TAAALLA2=====");
        const $waitingListButton = this.$('button[name="waiting_list_button"]');
        if ($waitingListButton.length) {
            console.log("1111 - Removing disabled attribute");
            $waitingListButton.removeAttr('disabled');
            console.log("Button after removing disabled:", $waitingListButton);
        } else {
            console.log("2222 - Setting primary button disabled state");
            this.$('button.btn-primary').attr('disabled', this._getTotalTicketCount() === 0);
        }
    },
});

export default publicWidget.registry.ticketDetailsWidget;
