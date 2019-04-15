odoo.define('website_event_track_advanced.acceptance', function (require) {

    $(function() {
        // Disable buttons if not accepted and vise versa
        function toggleSubmit(val) {
            $('#application-submit-button').prop('disabled', val);
            $('#application-submit-button-send').prop('disabled', val);
        }
        toggleSubmit(true);
        $('#privacy_acceptance').prop('checked', false);
        $('#privacy_acceptance').on('click', function() {
            toggleSubmit(!this.checked);
        });
    });
});
