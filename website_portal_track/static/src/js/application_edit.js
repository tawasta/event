$(function() {

    // Disable help boxes
    $('#track-application-form').find('p.alert').each(function() {
        $(this).hide();
    });

    // Disable application type selection
    $('#application_type').prop('disabled', true);

    // Hide attachment div
    $('#track-application-application-attachment-div').hide();

    // Disable target group selection
    $('#target_group_select').prop('disabled', true);

    // Disable all contact inputs
    $('#track-application-contact-div').removeClass('panel-primary');
    $('#track-application-contact-div').addClass('panel-default');

    $('#track-application-contact-div').find('input').each(function() {
        $(this).prop('disabled', true);
    });

    // Disable all speaker inputs
    $('#track-application-speakers-div').removeClass('panel-primary');
    $('#track-application-speakers-div').addClass('panel-default');

    $('#track-application-speakers-div').find('input').each(function() {
        $(this).prop('disabled', true);
    });

    // Hide speaker adding button
    $('#add_speaker').hide();

});