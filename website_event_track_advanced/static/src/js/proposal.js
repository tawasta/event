$(function() {

    function wordCount( val ){
        var wom = val.match(/\S+/g);
        return {
            charactersNoSpaces : val.replace(/\s+/g, '').length,
            characters         : val.length,
            words              : wom ? wom.length : 0,
            lines              : val.split(/\r*\n/).length
        };
    }

    $('#track-application-application-description-field').keyup(function(e){
        console.log(wordCount(this.value).words);
    })

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