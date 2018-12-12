odoo.define('agenda', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');
    var loadingScreen = require('website_utilities.loader').loadingScreen;

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

    // Mute not selected target groups on click
    $('#agenda-target-group-filter .btn').click(function(ev) {
        ev.preventDefault();

        // Mute all
        $('.event-track-content').addClass('text-muted');

        var active = $(this).hasClass('btn-primary');
        var target_group = false;

        // De-select selected
        $( "#agenda-target-group-filter .btn-primary" ).each(function( index ) {
            $(this).removeClass('btn-primary');
            $(this).addClass('btn-default');
        });
        $("#agenda-tag-filter .btn-primary" ).each(function( index ) {
            $(this).removeClass('btn-primary');
            $(this).addClass('btn-default');
        });

        if(!active){
            $(this).removeClass('btn-default');
            $(this).addClass('btn-primary');
            target_group = $(this).attr('value');
        }

        if (target_group) {
            // Unmute matching
            var tracks_not_matching = $(".track-td-targetgroup[name='"+target_group+"']").closest('.event-track-content');
            $(tracks_not_matching).addClass('text-muted');
        }
        else {
            // Unmute all
            $('.event-track-content').removeClass('text-muted');
        }
    });

    // Mute not selected tags on click
    $('#agenda-tag-filter .btn').click(function(ev) {
        ev.preventDefault();

        // Mute all
        $('.event-track-content').addClass('text-muted');

        var active = $(this).hasClass('btn-primary');
        var tag = false;

        // De-select selected
        $("#agenda-tag-filter .btn-primary" ).each(function( index ) {
            $(this).removeClass('btn-primary');
            $(this).addClass('btn-default');
        });
        $( "#agenda-target-group-filter .btn-primary" ).each(function( index ) {
            $(this).removeClass('btn-primary');
            $(this).addClass('btn-default');
        });

        if(!active){
            $(this).removeClass('btn-default');
            $(this).addClass('btn-primary');
            tag = $(this).attr('name');
        }

        if (tag) {
            // Unmute matching
            var tracks_not_matching = $(".track-td-tags[name*='"+tag+"']").closest('.event-track-content');
            $(tracks_not_matching).removeClass('text-muted');
        }
        else {
            // Unmute all
            $('.event-track-content').removeClass('text-muted');
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

    // Sticky elements
    $('.agenda-table').stickyTableHeaders();

    // Force sidescroll update
    var lastScrollLeft = 0;
    $('.table-responsive').scroll(function() {
        var documentScrollLeft = $(this).scrollLeft();
        if (lastScrollLeft != documentScrollLeft) {
            lastScrollLeft = documentScrollLeft;

            $(window).trigger('resize.stickyTableHeaders');
        }
    });

    $('.print-event-program').click(function() {
        window.print();
     });
});
