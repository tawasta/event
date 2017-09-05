$(function() {

    // Turn the whole tr into a link
    $('#event_track_list tr').click(function() {
        window.location = $(this).data("href");
    });
});