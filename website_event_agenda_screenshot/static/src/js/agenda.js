odoo.define('website_event_agenda_screenshot.html2canvas', function (require) {

    $(function() {
        $("#screenshot-event-program").click(function() {
            var container = $(this).parent().parent();
            var target = container.find('.agenda-day-content:first')[0];

            html2canvas(target).then(canvas => {
                // Create a link and "click" it
                var link = document.createElement('a');
                link.href = canvas.toDataURL("image/png");
                link.download = 'event_schedule.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        });
    });

});
