	odoo.define('website_event_track_advanced.agenda_day_content', function (require) {
	"use strict";

	var core = require('web.core');

	$(function(){
		$(".wrapper1").scroll(function(){
        $(".wrapper2")
            .scrollLeft($(".wrapper1").scrollLeft());
            console.log('Päästäänkö tähän?')
    });
    $(".wrapper2").scroll(function(){
    	console.log("Meneekö edes toisen function sisälle?")
        $(".wrapper1")
            .scrollLeft($(".wrapper2").scrollLeft());
            console.log("Entäs tänne?")
    });
});
});