$(function() {

    workshop_goals = CKEDITOR.replace('workshop_goals');
    workshop_schedule = CKEDITOR.replace('workshop_schedule');

    workshop_goals.on('instanceReady', function(){
        var word_limit = 200;

        wordCounter(false, workshop_goals.getData(), $('#workshop_goals_word_counter'), word_limit);

        this.on('key', function(event){
            setTimeout(function () {
                wordCounter(event, workshop_goals.getData(), $('#workshop_goals_word_counter'), word_limit);
            }, 0);
        });
    });

    workshop_goals.on('paste', function(event) {
        var word_limit = 200;

        // The timeout is necessary so the content will have the pasted info before calculating words
        setTimeout(function () {
            wordCounter(event, workshop_goals.getData(), $('#workshop_goals_word_counter'), word_limit);
        }, 0);
    })

});