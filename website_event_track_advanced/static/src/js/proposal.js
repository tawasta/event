$(function() {

    // Add speaker (contact) row(s)
    $('#add_contact').click(function() {
        // Clone the first row
        row = $('#track-application-speakers-input-row').clone().appendTo('#track-application-speakers-input-div');

        // Clear the values
        row.find("input[type='text']").val("");
        row.find("input[type='text']").name("test"+"[2]");
    });

    // Disable or enable webinar info textarea
    $('#track-application-webinar-selection-field').change(function(){
        disabled = parseInt($('#track-application-webinar-selection-field').val());
        $('#track-application-webinar-info-field').prop('disabled', !disabled);
    })

});