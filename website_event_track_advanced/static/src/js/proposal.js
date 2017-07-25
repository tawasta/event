$(function() {

    // Add a '*' to required fields
    $( "*[required='true']" ).each(function( index ) {
        var label = $('label[for="'+$(this).attr('name')+'"]');
        label.addClass('required-label text-primary');
    });

    function wordCount(val){
        var regex = /\s+/gi;
        var wordCount = val.trim().replace(regex, ' ').split(' ').length;

        return wordCount;
    }

    /*
    $('#track-application-application-description-field').keyup(function(e){
        console.log(wordCount(this.value).words);
    })
    */

    // Replace textarea-fields with CKEditor
    track_content = CKEDITOR.replace('track_content');
    target_group_info = CKEDITOR.replace('target_group_info');
    webinar_info = CKEDITOR.replace('webinar_info');
    extra_info = CKEDITOR.replace('extra_info');

    track_content.on('instanceReady', function(){
        this.document.on('keydown', function(event){
            // var content = this.getBody().getText();
            var content = track_content.getData();
            word_count = wordCount(content);

            keycode = event.data.getKey();

            // 8 = backspace
            // 46 = del
            word_limit = 300;
            if(word_count >= word_limit
             && keycode != 8 && keycode != 46){
                event.data.preventDefault();
                $('#target_group_info_word_counter').addClass("text-danger");
            }
            else {
                $('#target_group_info_word_counter').removeClass("text-danger");
            }
            $('#target_group_info_word_count').text(word_count);
        });
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