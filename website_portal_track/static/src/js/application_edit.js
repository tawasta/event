$(function() {

    // Disable application type selection
    $('#application_type').prop('disabled', true);

    // Hide attachment div
    $('#track-application-application-attachment-div').hide();

    // Disable target group selection
    $('#target_group_select').prop('disabled', true);

    // Hide contact info box
    $('#track-application-contact-div p.alert').hide();

    // Disable all contact inputs
    $('#track-application-contact-div').find('input').each(function() {
        $(this).prop('disabled', true);
    });

    // Hide speakers info box
    $('#track-application-speakers-div p.alert').hide();

    // Disable all speaker inputs
    $('#track-application-speakers-div').find('input').each(function() {
        $(this).prop('disabled', true);
    });

    // Hide speaker adding button
    $('#add_speaker').hide();

});