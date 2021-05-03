odoo.define('website_event_waiting_list.website_event', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');

    var _t = core._t;
    var WebsiteEvent = require('website_event.website_event');
    // Catch registration form event, because of JS for attendee details

    var EventWaitingForm = WebsiteEvent.include({
        /**
         * @override
         */
        on_click: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest('form');
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var waiting_list = false;
            if ($($button).attr('name') == "waiting_list") {
                waiting_list = true;
            }
            var post = {};
            $('#registration_form table').siblings('.alert').remove();
            $('#registration_form select').each(function () {
                post[$(this).attr('name')] = $(this).val();
            });
            var tickets_ordered = _.some(_.map(post, function (value, key) { return parseInt(value); }));
            if (!tickets_ordered && !waiting_list) {
                $('<div class="alert alert-info"/>')
                    .text(_t('Please select at least one ticket.'))
                    .insertAfter('#registration_form table');
                return new Promise(function () {});
            } else {
                $button.attr('disabled', true);
                return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
                    var $modal = $(modal);
                    $modal.modal({backdrop: 'static', keyboard: false});
                    $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                    $modal.appendTo('body').modal();
                    $modal.on('click', '.js_goto_event', function () {
                        $modal.modal('hide');
                        $button.prop('disabled', false);
                    });
                    $modal.on('click', '.close', function () {
                        $button.prop('disabled', false);
                    });
                });
            }
        },
        // $('#confirm_waiting_modal').on('show.bs.modal', function(e) {

        // })
    });
    return EventWaitingForm;
});
