odoo.define('website_event_agenda_screenshot.html2canvas', function (require) {

    $(function() {
        $("#screenshot-event-program").click(function() {
            var container = $(this).parent().parent();
            var target = container.find('.agenda-day-content:first')[0];

            html2canvas(target).then(canvas => {
                window.open(canvas.toDataURL("image/png"));
            });
        });
    });

});
