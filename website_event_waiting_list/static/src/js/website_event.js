/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { Modal } from "bootstrap";

// Ensimmäinen tarkistetaan ja varmennetaan, että EventRegistrationFormInstance on määritelty oikein
const EventRegistrationFormInstance = publicWidget.registry.EventRegistrationFormInstance;

if (EventRegistrationFormInstance) {
    EventRegistrationFormInstance.include({
        /**
         * @override
         */
        start: function () {
            var self = this;
            const post = this._getFormPostData();
            const noTicketsOrdered = Object.values(post).map((value) => parseInt(value)).every(value => value === 0);
            var res = this._super.apply(this, arguments).then(function () {
                $('#registration_form .a-submit')
                    .off('click')
                    .click(function (ev) {
                        self._onSubmitClick(ev);
                    })
                    .prop('disabled', noTicketsOrdered);
                
                // Poista disabled attribuutti waiting_list_buttonista
                const $waitingListButton = $('#registration_form button[name="waiting_list_button"]');
                if ($waitingListButton.length) {
                    $waitingListButton.removeAttr('disabled');
                }
            });
            return res;
        },

        _getFormPostData: function () {
            var post = {};
            $('#registration_form select').each(function () {
                post[$(this).attr('name')] = $(this).val();
            });
            return post;
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onSubmitClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest('form');
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            const post = this._getFormPostData();
            $button.attr('disabled', true);
            return jsonrpc($form.attr('action'), post).then(function (modal) {
                var $modal = $(modal);
                $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                $modal.appendTo(document.body);
                const modalElement = $modal[0];
                const modalInstance = new Modal(modalElement, { backdrop: 'static', keyboard: false });
                modalInstance.show();
                $modal.on('hidden.bs.modal', function () {
                    $button.prop('disabled', false);
                });
                $modal.on('click', '.js_goto_event, .btn-close', function () {
                    modalInstance.hide();
                });
            });
        },
    });
}

export default EventRegistrationFormInstance;
