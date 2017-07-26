$(function() {

    target_group_info = CKEDITOR.replace('target_group_info');

    target_group_info.on('instanceReady', function(){
        word_limit = 300;

        wordCounter(false, target_group_info.getData(), $('#target_group_info_word_counter'), word_limit);

        this.on('key', function(event){
            wordCounter(event, target_group_info.getData(), $('#target_group_info_word_counter'), word_limit);
        });
    });

    target_group_info.on('paste', function(event) {
        // The timeout is necessary so the content will have the pasted info before calculating words
        setTimeout(function () {
            wordCounter(event, target_group_info.getData(), $('#target_group_info_word_counter'), word_limit);
        }, 0);
    })

});