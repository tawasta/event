$(function() {

    extra_info = CKEDITOR.replace('extra_info');

    extra_info.on('instanceReady', function(){
        word_limit = 300;

        wordCounter(false, extra_info.getData(), $('#extra_info_word_counter'), word_limit);

        this.on('key', function(event){
            wordCounter(event, extra_info.getData(), $('#extra_info_word_counter'), word_limit);
        });
    });

    extra_info.on('paste', function(event) {
        // The timeout is necessary so the content will have the pasted info before calculating words
        setTimeout(function () {
            wordCounter(event, extra_info.getData(), $('#extra_info_word_counter'), word_limit);
        }, 0);
    })

});