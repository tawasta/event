odoo.define('website_event_agenda_tag_cloud.tag_cloud', function (require) {

    var ajax = require('web.ajax');

    var action = '/event/get/keywords';
    var values = {'event_id': $('#event-id').text()};

    ajax.jsonRpc(action, 'call', values).then(function(data){
        var keywords = data['keywords'];
        $('#tag-cloud').jQCloud(keywords,
            {
                height: 350,
                autoResize: true
            }
        );

        $('#tag-cloud').on('click', '.jqcloud-word', function(){
            tag_id = $(this).data('keyword-id');

            // Toggle active
            $(this).toggleClass('active');

            // All active keywords
            active_keywords = $(".jqcloud-word.active").map(function() {
                return $(this).data('keyword-id');
            }).get();

            if(active_keywords){
                // Mute or unmute tracks
                $('td.event_track').each(function(){
                    var tags = $(this).find('.track-td-tags').data('track-ids');
                    var match = false;

                    if(!tags){
                        // No reason to match. Continue
                        return;
                    }

                    // Check if any of the tags are in keywords
                    jQuery.each(tags, function( i, val) {
                        if($.inArray(val, active_keywords) >= 0){
                            match = true;
                            // We have a match, break the inner loop
                            return false;
                        }
                    });

                    $(this).toggleClass('muted', !match);
                });
            } else {
                // Unmute all
                $('td.event_track').removeClass('muted');
            }
        });
    });

});
