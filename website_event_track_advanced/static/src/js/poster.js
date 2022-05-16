odoo.define("poster", function (require) {
    $(".track-carousel-image").click(function () {
        $("#poster-carousel").toggleClass("carousel-collapsed");
    });
});
