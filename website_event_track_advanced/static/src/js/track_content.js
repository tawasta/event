$(function() {

    if($('#track_content').length){
        track_content = CKEDITOR.replace('track_content');

        track_content.on('instanceReady', function(){
            var word_limit = 300;

            wordCounter(false, track_content.getData(), $('#track_content_word_counter'), word_limit);

            this.on('key', function(event){
                wordCounter(event, track_content.getData(), $('#track_content_word_counter'), word_limit);
            });
        });

        track_content.on('paste', function(event) {
            var word_limit = 300;

            // The timeout is necessary so the content will have the pasted info before calculating words
            setTimeout(function () {
                wordCounter(event, track_content.getData(), $('#track_content_word_counter'), word_limit);
            }, 0);
        })

        // Check the content word limit
        $('.application-submit-button').click(function(event) {
            var word_limit = 300;
            var field_content = CKEDITOR.instances['track_content'].getData();
            var word_count = wordCount(field_content);

            if(word_count == 0 || word_count > word_limit){
                event.preventDefault();
                $('#track-application-track_content-error-div').removeClass('hidden');

                $('html, body').animate({
                    scrollTop: $('#track-application-application-info-content').offset().top
                }, 500);
            }
            else {
                $('#track-application-track_content-error-div').addClass('hidden');
            }
        })
    }


});