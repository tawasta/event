odoo.define('proposal', function (require) {
    var _t = require('web.core')._t;

    // Add a '*' to required fields
    $( "*[required]" ).each(function( index ) {
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
    $('#add_speaker').click(function() {
        // Clone the first row
        row = $('#track-application-speakers-input-row').clone().appendTo('#track-application-speakers-input-div');
        row.removeAttr('id');
        row.find('button').removeAttr('disabled');

        input_index =  parseInt($('#track-application-speakers-input-index').val()) + 1;
        $('#track-application-speakers-input-index').val(input_index);

        // Clear the values
        row.find('input').val('');

        // Add an unique name
        row.find('input').each(function() {
            property_value = $(this).prop('name');
            index_name = property_value.substring(0, property_value.length - 3) + '[' + input_index + ']';
            $(this).prop('name', index_name);
        });
    });

    // Remove speaker rows
    $(document).on('click', '.btn-remove-speaker', function() {
        var confirm_message = _t("Are you sure you want to delete this speaker?");

         if (confirm(confirm_message)) {
            $(this).parent().remove();
         }
    });

    // Disable or enable webinar info textarea
    /**
    $('#track-application-webinar-selection-field').change(function(){
        disabled = parseInt($('#track-application-webinar-selection-field').val());
        $('#webinar_info').prop('disabled', !disabled);
    })
    **/

    $('#application_type').change(function(){
        $('#application_type_description').html($('#application_type option:selected').attr('title'));
        var application_type = $('#application_type option:selected').val();

        workshop = application_type == 'workshop';
        // Toggle display by form type
        $('#track-application-workshop-div').toggle(workshop);

        // Remove or add required-class from hidden fields
        if(workshop){
            $('#track-application-workshop-div').find('input[required_disabled]').each(function() {
                $(this).attr('required', true);
            });
        } else {
            $('#track-application-workshop-div').find('input[required]').each(function() {
                $(this).removeAttr('required');
                $(this).attr('required_disabled', true);
            });
        }
    });

    $(function() {
        $('#application_type').trigger('change');
    });

    // Allow collapsing panel items
    $( ".panel-heading" ).click(function() {
        $(this).next().slideToggle('800', function() {});
    });

    // De-collapse all elements on submit (to show errors)
    // TODO: only de-collapse if has errors
    $('#application-submit-button').click(function() {
        $('#track-application-form').find('div.panel-body').each(function() {
            if($(this).is(":hidden")){
                $(this).slideToggle('800', function() {});
            }
        });
    })

    // Suggest the contact as a speaker
    $('#track-application-contract-input-div input').change(function(){
        var changed_field = $(this).attr('name').substr(8);
        var corresponding_field_name = 'speaker_' + changed_field + '[0]';
        var corresponding_field = $("input[name='" + corresponding_field_name + "']" );

        if(corresponding_field.val() == ''){
            corresponding_field.val($(this).val())
        }
    });

});
