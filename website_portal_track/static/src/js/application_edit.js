$(function() {

    var application_state = $('#application_state').val();

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
        var field_name = $(this).attr("name");

        // Don't disable the template
        if(field_name){
            return true;
        }

        $(this).prop('disabled', true);
    });

    if(application_state != 'draft'){
        // Disable application type selection
        $('#application_type').prop('disabled', true);

        // Hide attachment div
        $('#track-application-application-attachment-div').hide();

        // Disable target group selection
        $('#target_group_select').prop('disabled', true);

        // Hide speaker adding button
        $('#add_speaker').hide();

        // Disable all speaker inputs
        $('#track-application-workshop-div').removeClass('panel-warning');
        $('#track-application-workshop-div').addClass('panel-default');

        $('#track-application-workshop-div').find('input').each(function() {
            $(this).prop('disabled', true);
        });

        // Enable workshop_participants
        $('#workshop_participants').prop('disabled', false);
    }
});