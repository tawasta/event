$(function() {

    // Add a '*' to required fields
    $( "*[required='true']" ).each(function( index ) {
        var label = $('label[for="'+$(this).attr('name')+'"]');
        label.addClass('required-label text-primary');
    });

    // Counts words in the given content
    window.wordCount = function(val){
        var regex = /\s+/gi;
        var trimmed = val.trim().replace(regex, ' ').split(' ');

        if(trimmed == "") word_count = 0;
        else word_count = trimmed.length;

        return word_count;
    }

    // Adds word-counter properties for textarea.
    // The counter_object has to have a span-element inside itself for the counter
    window.wordCounter = function (event, content, counter_object, word_limit){
        keycode = false;
        if(event){
            keycode = event.data.keyCode;
        }

        word_count = wordCount(content);

        // Update word count class
        if(word_count >= word_limit){
            counter_object.addClass("text-danger");
            // This is not working for some reason
            counter_object.effect("shake", {times:3}, 800 );

            // Disable enter and space when word count is full
            // 13 = enter
            // 31 = space
            // 1114198 = Ctrl-v
            var keycode_list = [13, 32, 1114198];
            if ($.inArray(keycode, keycode_list) >= 0) {
                event.cancel();
            }
        } else {
            counter_object.removeClass("text-danger");
        }

        // Update the counter number
        counter_object.find("span").text(word_count + "/" + word_limit);
    }

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
    /**
    $('#track-application-webinar-selection-field').change(function(){
        disabled = parseInt($('#track-application-webinar-selection-field').val());
        $('#webinar_info').prop('disabled', !disabled);
    })
    **/

});