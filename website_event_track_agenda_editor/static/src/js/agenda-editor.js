odoo.define('website_event_track_agenda_editor.agenda', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    // Schedule modal submit
    $('.track-schedule-action').on('show.bs.modal', function(e) {
        $(this).find('#track_id').val($(e.relatedTarget).data('track'));
    });

    // Drag & Drop events
    $('.event_track').on('mouseover', function(ev) {
        ev.preventDefault();
    });

    // Starting to track an element
    $('.event_track').on('dragstart', function(ev) {
        ev.originalEvent.dataTransfer.setData('text/html', null);
        ev.originalEvent.dataTransfer.setData('old_track', $(this).attr('name'));
    });

    // Preparing for drop
    $('.event_track').on('dragover', function(ev) {
        ev.preventDefault();
        $(this).addClass('active');
    });

    $('.event-track-unassign').on('dragover', function(ev) {
        ev.preventDefault();
        $(this).addClass('active');
    });

    $('.event_track').on('dragleave', function(ev) {
        ev.preventDefault();
        $(this).removeClass('active');
    });

    $('.event-track-unassign').on('dragleave', function(ev) {
        ev.preventDefault();
        $(this).addClass('active');
    });

    // Dropping Presentation over Presentation
    $('.agenda-day-content .event_track').on('drop', function(ev) {
        // Don't run this if no access rights. Backend will check the access right,
        // but JS console will complain about session
        ev.preventDefault();

        var old_track = ev.originalEvent.dataTransfer.getData('old_track');
        var new_track = $(this).attr('name');

        var action = "/event/track/move";
        var values = {'old_track_id': old_track, 'new_track_id': new_track};

        loadingScreen()
        ajax.jsonRpc(action, 'call', values).then(function(data){
            if(data == 200){
                // Success. Reload page to prevent sync problems
                location.reload();
            }
            else if(data == 500){
                $.unblockUI();
                alert(_t("What you were trying to do is not implemented yet. Sorry!"));
            }
            else if(data == 403){
                // Unexpected error
                $.unblockUI();
                alert(_t("Error while trying to move the presentation. Please reload the page!"));
            }
        });
    });

   // Dropping Presentation over Header
    $('.event-track-unassign').on('drop', function(ev) {
        // Don't run this if no access rights. Backend will check the access right,
        // but JS console will complain about session
        ev.preventDefault();

        var old_track = ev.originalEvent.dataTransfer.getData('old_track');

        var action = "/event/track/unassign";
        var values = {'old_track_id': old_track};
        var action = "/event/track/unassign";

        loadingScreen();
        ajax.jsonRpc(action, 'call', values).then(function(data){
            if(data == 200){
                // Success. Reload page to prevent sync problems
                location.reload();
            }
            else if(data == 500){
                $.unblockUI();
                alert(_t("What you were trying to do is not implemented yet. Sorry!"));
            }
            else if(data == 403){
                // Unexpected error
                $.unblockUI();
                alert(_t("Error while trying to unassign the presentation. Please reload the page!"));
            }
        });
    });
});
