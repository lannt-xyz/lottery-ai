$(document).ready(function() {
    // get all keys from local storage
    var keys = Object.keys(localStorage);
    // find all element has class `form-control` and set their value from local storage
    $('.form-control').each(function() {
        var key = $(this).attr('data-key');
        if (keys.includes(key)) {
            var value = localStorage.getItem(key);
            $(this).val(value);
        }
    });

    $('#btn-save').click(function() {
        // find all control with class 'form-control' and get their values
        var data = {};
        $('.form-control').each(function() {
            var key = $(this).attr('data-key');
            var value = $(this).val();
            data[key] = value;
        });

        // based on data store the values to local storage one by one
        for (var key in data) {
            var value = data[key];
            localStorage.setItem(key, value);
        }

        // show success message by using toastr
        toastr.success('Settings saved successfully');
    });
});