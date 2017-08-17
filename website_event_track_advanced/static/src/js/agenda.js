odoo.define('agenda', function (require) {
    var _t = require('web.core')._t;

    // Add ending times to timeslots
    // This is easier to do after the creation of the table due the agenda array structure
    $('.agenda-timeslot-row').each(function() {
        var this_timeslot = $(this).find('.agenda-timeslot-time');
        var next_timeslot = $(this).next().find('.agenda-timeslot-time');

        if(next_timeslot){
            var timeslot_range = this_timeslot.text() + " - " + next_timeslot.text();
            this_timeslot.text(timeslot_range);
        };
    });
});
