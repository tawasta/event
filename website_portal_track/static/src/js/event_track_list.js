$(function() {

    // Turn the whole tr into a link
    $('#event_track_list .td-submit').click(function() {
        window.location = $(this).data("href");
    });

    // Confirmation dialog
    $('#track-confirm-action').on('show.bs.modal', function(e) {
        $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));

        $(this).find('.modal-track-action').text( $(e.relatedTarget).data('action') );
        $(this).find('.modal-track-title').text( $(e.relatedTarget).data('title') );
    });
});