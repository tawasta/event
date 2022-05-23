odoo.define("poster", function () {
    "use strict";
    $(".track-carousel-image").click(function () {
        $("#poster-carousel").toggleClass("carousel-collapsed");
    });
});
