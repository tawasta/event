odoo.define('agenda', function (require) {
    var _t = require('web.core')._t;

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

    // Allow collapsing tags list
    $('#tags-collapse-button').click(function(){
        $('#tags-collapse').fadeToggle();
    });

    // Allow days
    $(".date-heading").click(function() {
        $(this).find('.chevron-toggle').toggle();
        $(this).next().slideToggle();
    });

    $('div.event-track-content')
        .mouseenter(function() {
            var title = $(this).find('.extra-info').html();
            $(this).attr('data-original-title', title);
            $(this).tooltip();
        })
});
