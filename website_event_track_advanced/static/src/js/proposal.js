$(function() {

    // Add speaker (contact) row(s)
    $('#add_contact').click(function() {
        $('#track-application-speakers-input-row').clone().appendTo('#track-application-speakers-input-div').find("input[type='text']").val("");;
    });

    // Disable or enable webinar info textarea
    $('#track-application-webinar-selection-field').change(function(){
        disabled = parseInt($('#track-application-webinar-selection-field').val());
        $('#track-application-webinar-info-field').prop('disabled', !disabled);
    })

});