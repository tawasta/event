$(function() {

    // Add a '*' to required fields
    $( "*[required='true']" ).each(function( index ) {
        var label = $('label[for="'+$(this).attr('name')+'"]');
        label.addClass('required-label text-primary');
    });

    function wordCount(val){
        var regex = /\s+/gi;
        var trimmed = val.trim().replace(regex, ' ').split(' ');

        if(trimmed == "") word_count = 0;
        else word_count = trimmed.length;

        return word_count;
    }

    function wordCounter(event, word_limit){
        keycode = false;
        if(event){
            keycode = event.data.keyCode;
        }

        var content = track_content.getData();
        word_count = wordCount(content);

        // Update word count class
        if(word_count >= word_limit){
            $('#target_group_info_word_counter').addClass("text-danger");
            // This is not working for some reason
            $('#target_group_info_word_counter').effect("shake", {times:3}, 800 );

            // Disable enter and space when word count is full
            // 13 = enter
            // 31 = space
            // 1114198 = Ctrl-v
            var keycode_list = [13, 32, 1114198];
            if ($.inArray(keycode, keycode_list) >= 0) {
                event.cancel();
            }
        } else {
            $('#target_group_info_word_counter').removeClass("text-danger");
        }

        // Update the counter number
        $('#target_group_info_word_count').text(word_count + "/" + word_limit);
    }

    // Replace textarea-fields with CKEditor
    track_content = CKEDITOR.replace('track_content');
    target_group_info = CKEDITOR.replace('target_group_info');
    webinar_info = CKEDITOR.replace('webinar_info');
    extra_info = CKEDITOR.replace('extra_info');

    track_content.on('instanceReady', function(){
        word_limit = 5;
        wordCounter(false, word_limit);

        this.on('key', function(event){
            wordCounter(event, word_limit);
        });

        this.on('paste', function(event) {
            wordCounter(event, word_limit);
        })
    });


    // Add speaker (contact) row(s)
    $('#add_contact').click(function() {
        // Clone the first row
        row = $('#track-application-speakers-input-row').clone().appendTo('#track-application-speakers-input-div');
        row.removeAttr('id');

        input_index =  parseInt($('#track-application-speakers-input-index').val()) + 1;
        $('#track-application-speakers-input-index').val(input_index);

        // Clear the values
        row.find("input").val("");

        // Add an unique name
        row.find("input").each(function() {
            property_value = $(this).prop('name');
            console.log(property_value);
            index_name = property_value.substring(0, property_value.length - 3) + '[' + input_index + ']';
            console.log(index_name);
            $(this).prop('name', index_name);
        });
    });

    // Disable or enable webinar info textarea
    $('#track-application-webinar-selection-field').change(function(){
        disabled = parseInt($('#track-application-webinar-selection-field').val());
        $('#track-application-webinar-info-field').prop('disabled', !disabled);
    })

});