$(function() {

    webinar_info = CKEDITOR.replace('webinar_info');

    webinar_info.on('instanceReady', function(){
        var word_limit = 200;

        wordCounter(false, webinar_info.getData(), $('#webinar_info_word_counter'), word_limit);

        this.on('key', function(event){
            setTimeout(function () {
                wordCounter(event, webinar_info.getData(), $('#webinar_info_word_counter'), word_limit);
            }, 0);
        });
    });

    webinar_info.on('paste', function(event) {
        var word_limit = 200;

        // The timeout is necessary so the content will have the pasted info before calculating words
        setTimeout(function () {
            wordCounter(event, webinar_info.getData(), $('#webinar_info_word_counter'), word_limit);
        }, 0);
    })

});