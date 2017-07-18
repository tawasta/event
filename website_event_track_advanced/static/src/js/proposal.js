$(function() {

    $('#add_contact').click(function() {
        var newContact = `
            <div class='form-group col-lg-6'>
                <label class='control-label'>Name</label>
                <input type="text" name="contact_name" class="form-control"/>
            </div>
            <div class="form-group col-lg-6">
                <label class="control-label">Email</label>
                <input type="text" name="contact_email" class="form-control"/>
            </div>
        `;
        $('#contact_info').append(newContact);
    });

});