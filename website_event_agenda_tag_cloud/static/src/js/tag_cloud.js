odoo.define('website_event_agenda_tag_cloud.tag_cloud', function (require) {

    var ajax = require('web.ajax');

    var action = '/event/get/keywords';
    var values = {'event_id': $('#event-id').text()};

    ajax.jsonRpc(action, 'call', values).then(function(data){
        var keywords = data['keywords'];
        $('#tag-cloud').jQCloud(keywords, {width: 550, height: 350});
    });

    $('.keyword-clickable').click(function(event) {
        tag_id = $(this).data('keyword-id');
        console.log('Clicked ' + tag_id);
    });

});
