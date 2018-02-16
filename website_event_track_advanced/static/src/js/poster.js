odoo.define('poster', function (require) {
    var _t = require('web.core')._t;
    var ajax = require('web.ajax');

    $('.track-carousel-image').click(function() {
        $('#poster-carousel').toggleClass('carousel-collapsed');
    });
});
