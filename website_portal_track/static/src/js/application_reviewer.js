$(function() {

    // Disable help boxes
    $('#track-application-form').find('p.alert').each(function() {
        $(this).hide();
    });

    // Hide attachment div
    $('#track-application-application-attachment-div').hide();

    // Disable inputs
    $('#track-application-form').find('input,select,textarea').each(function() {
        $(this).prop('disabled', true);
    });

    // Enable csrf token
    $('#csrf_token').removeAttr('disabled');

    // Enable review inputs
    $('#track-application-review-div').find('input').each(function() {
        $(this).removeAttr('disabled');
    });

});