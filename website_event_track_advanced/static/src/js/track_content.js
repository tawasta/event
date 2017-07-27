$(function() {

    track_content = CKEDITOR.replace('track_content');

    track_content.on('instanceReady', function(){
        var word_limit = 300;

        wordCounter(false, track_content.getData(), $('#track_content_word_counter'), word_limit);

        this.on('key', function(event){
            setTimeout(function () {
                wordCounter(event, track_content.getData(), $('#track_content_word_counter'), word_limit);
            }, 0);
        });
    });

    track_content.on('paste', function(event) {
        var word_limit = 300;

        // The timeout is necessary so the content will have the pasted info before calculating words
        setTimeout(function () {
            wordCounter(event, track_content.getData(), $('#track_content_word_counter'), word_limit);
        }, 0);
    })

});