odoo.define('proposal', function (require) {
    var _t = require('web.core')._t;

    // Confirm language change
    $('.js_change_lang').click(function() {
        return confirm(_t("Are you sure? Any unsaved changes will be lost."));
    });

    /*
    // Add file name to attachment input button
    $(':file').change(function() {
        var label = $(this).val().replace(/\\/g, '/').replace(/.*\//, '');

        $('#attachment-label').text("(" + label + ")");
    });
    */

    // Remove attachment
    $('#btn-remove-attachment').click(function() {
        //$('#attachment-label').text('');
        $('#attachment-file').val('');
    });


    $('#attachment-file').bind('change', function(){
        if(!this.files[0]){
            return true;
        }

        var attachment_size = this.files[0].size;
        var max_size =  30 * 1024 * 1024;

        if(attachment_size > max_size){
            $('#attachment-label').text('');
            $('#attachment-file').val('');
            // Show the error div
            $('#track-application-attachment-error-div').removeClass('hidden');
        }
        else {
            // Hide the error div
            $('#track-application-attachment-error-div').addClass('hidden');
        };
    });

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
        var keycode = false;
        if(event && event.data){
            keycode = event.data.keyCode;
        }

        var word_count = wordCount(content);

        // Update word count class
        if(word_count >= word_limit){
            counter_object.addClass("text-danger");

            // Disable enter and space when word count is full
            // 10 = enter
            // 13 = return
            // 31 = space
            // 1114198 = Ctrl-v
            var keycode_list = [10, 13, 32, 1114198];
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
        var row = $('#track-application-speakers-input-row').clone().appendTo('#track-application-speakers-input-div');
        row.removeAttr('id');
        row.find('button').removeAttr('disabled');

        input_index =  parseInt($('#track-application-speaker-input-index').val()) + 1;
        $('#track-application-speaker-input-index').val(input_index);

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
        $('#application_type_description').html($('#application_type option:selected').attr('description'));
        var application_type = $('#application_type option:selected').val();

        if(!application_type){
            $(".panel-body").hide();
            $("#track-application-type-div .panel-body").show();
        } else {
            $(".panel-body").fadeIn("slow");
        }

        workshop = application_type == 'workshop';
        // Toggle display by form type
        $('#track-application-workshop-div').toggle(workshop);

        // Remove or add required-class from hidden fields
        if(workshop){
            $('#track-application-workshop-div').find('input[required_disabled]').each(function() {
                $(this).attr('required', true);
            });
            $('#track-application-workshop-div').find('select[required_disabled]').each(function() {
                $(this).attr('required', true);
            });
        } else {
            $('#track-application-workshop-div').find('input[required]').each(function() {
                $(this).removeAttr('required');
                $(this).attr('required_disabled', true);
            });

            $('#track-application-workshop-div').find('select[required]').each(function() {
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
    $('.application-submit-button').click(function() {

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
