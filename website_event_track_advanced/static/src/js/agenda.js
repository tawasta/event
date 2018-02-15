odoo.define('agenda', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    // Make contains case insensitive
    // https://gist.github.com/jakebresnehan/2288330
    jQuery.expr[':'].Contains = function(a, i, m) {
     return jQuery(a).text().toUpperCase()
         .indexOf(m[3].toUpperCase()) >= 0;
    };

    $('#event-track-search').bind('keyup', function(){
        var change_text = $(this).val();
        $('.event-track-content').removeClass('text-muted');
        $('#event-track-search-summary').removeClass('hidden');

        if (change_text) {
            var tracks_matching = $(".event-track-content:Contains("+change_text+")");
            var tracks_not_matching = $(".event-track-content:not(:Contains("+change_text+"))");

            $('#event-track-found').text(tracks_matching.length);
            $(tracks_not_matching).addClass('text-muted');
        } else {
            $('#event-track-found').text(0);
            $('#event-track-search-summary').addClass('hidden');
        }
    });

    $('#target-groups-collapse .btn').click(function(ev) {
        ev.preventDefault();

        // Unmute all
        $('.event-track-content').removeClass('text-muted');

        var active = $(this).hasClass('btn-primary');
        var target_group = false;

        // De-select selected
        $( "#target-groups-collapse .btn-primary" ).each(function( index ) {
            $(this).removeClass('btn-primary');
            $(this).addClass('btn-default');
        });

        if(!active){
            $(this).removeClass('btn-default');
            $(this).addClass('btn-primary');
            target_group = $(this).attr('value');
        }

        // Mute not matching
        if (target_group) {
            var tracks_not_matching = $(".track-td-targetgroup[name!='"+target_group+"']").closest('.event-track-content');
            $(tracks_not_matching).addClass('text-muted');
        }
    });

    // Allow days
    $(".date-heading").click(function() {
        $(this).find('.chevron-toggle').toggle();
        $(this).parent().next().slideToggle();
    });

    $('div.event-track-content')
        .mouseenter(function() {
            var title = $(this).find('.extra-info').html();

            $(this).attr('data-original-title', title)
            .tooltip('fixTitle')
            .tooltip('show');
        })

    // Drag & Drop events
    $('.event_track').on('mouseover', function(ev) {
        ev.preventDefault();
    });

    // Starting to track an element
    $('.event_track').on('dragstart', function(ev) {
        console.log('dragging');
        ev.originalEvent.dataTransfer.setData('text/html', null);
        ev.originalEvent.dataTransfer.setData('old_track', $(this).attr('name'));
    });

    // Preparing for drop
    $('.event_track').on('dragover', function(ev) {
        ev.preventDefault();
    });

    // Dropping the element
    $('.event_track').on('drop', function(ev) {
        // Don't run this if no access rights. Backend will check the access right,
        // but JS console will complain about session

        ev.preventDefault();

        var old_track = ev.originalEvent.dataTransfer.getData('old_track');
        var new_track = $(this).attr('name');

        var action = "/event/track/move";
        var values = {'old_track_id': old_track, 'new_track_id': new_track};

        ajax.jsonRpc(action, 'call', values).then(function(data){
            if(data == 200){
                // Success. Reload page to prevent sync problems
                location.reload();
            }
            else if(data == 500){
                return false;
            }
            else if(data == 403){
                // Unexpected error
                alert(_t("Error while trying to move the presentation. Please reload the page!"));
            }
        });
    });

    $('.print-event-program').click(function() {
        window.print();
     });
});
