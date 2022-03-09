odoo.define('website_event_track_privacies.event_track_application', function (require) {

    $(function() {
        if ($(".privacy_acceptance")[0]){
            function toggleSubmit(val) {
                $('#application-submit-button').prop('disabled', val);
                $('#application-submit-button-send').prop('disabled', val);
            }
            toggleSubmit(true);
            $('.privacy_acceptance').prop('checked', false);
            $('.privacy_acceptance').on('click', function() {
                toggleSubmit(!this.checked);
            });
        }
    });
});
