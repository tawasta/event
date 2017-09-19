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

    // Hide speaker template
    $('#track-application-speakers-input-row').hide();

    $('#track-application-speakers-div').find('input').each(function() {
        var field_name = $(this).attr("name");

        // Don't disable the template
        if(field_name){
            // Remove comment to enable
            // return true;
        }

        $(this).prop('disabled', true);
    });

    // Enable speaker fields
    $('#add_speaker').click(function() {
        var last_div = $('#track-application-speakers-input-div .track-application-contact-input-row:last');

        last_div.show();

        last_div.find('input').each(function() {
            $(this).prop('disabled', false);
        })
    });

    // Disable new speaker
    $('#track-application-speakers-input-row').prop('disabled', true);

    if(application_state != 'draft'){
        // Disable application type selection
        $('#application_type').prop('disabled', true);

        // Hide attachment div
        $('#track-application-application-attachment-div').hide();

        // Disable all speaker inputs
        $('#track-application-workshop-div').removeClass('panel-warning');
        $('#track-application-workshop-div').addClass('panel-default');

        // Disable target group selection
        $('#target_group_select').prop('disabled', true);
    };

    if(application_state != 'draft' && application_state != 'announced'){
        // Hide speaker adding button
        $('#add_speaker').hide();

        // Enable workshop_participants
        $('#workshop_participants').prop('disabled', false);

        $('#track-application-workshop-div').find('input').each(function() {
            $(this).prop('disabled', true);
        });

        // Disable inputs, except content editing
        $('#track-application-form').find('input,select').each(function() {
            $(this).prop('disabled', true);
        });
    };

    if(application_state == 'cancel' || application_state == 'refused' || application_state == 'published'){
        // Disable everything
        $('#track-application-form').find('input,select,textarea').each(function() {
            $(this).prop('disabled', true);
        });
    };

});