"use strict";

// A very simple method to check the strength of a password
const validatePassword = function (input) {
    const value = input.value;
    if (value === '') {
        return {
            valid: false,
            message: 'Password is required',
        };
    }

    if (value.search(/[a-z]/) < 0 && value.search(/[A-Z]/) < 0) {
        return {
            valid: false,
            message: 'Password must have at least one character',
        };
    }

    if (value === value.toLowerCase()) {
        return {
            valid: false,
            message: 'Password must have at least one uppercase character',
        };
    }

    if (value === value.toUpperCase()) {
        return {
            valid: false,
            message: 'Password must have at least one lowercase character',
        };
    }

    if (value.search(/[0-9]/) < 0) {
        return {
            valid: false,
            message: 'Password must have at least one digit',
        };
    }

    if (value.length < 8) {
        return {
            valid: false,
            message: 'Password must have at least 8 characters',
        };
    }

    return {valid: true};
};

// Class Definition
var KTLogin = function () {
    var _buttonSpinnerClasses = 'spinner spinner-right spinner-white pr-15';

    var _handleFormReset = function _handleFormReset() {
        var form = KTUtil.getById('kt_user_reset_form');
        var formSubmitUrl = KTUtil.attr(form, 'action') + $('#uidb64').val() + '/' + $('#token').val();
        var formSubmitButton = KTUtil.getById('kt_user_reset_form_submit_button');

        if (!form) {
            return;
        }

        FormValidation.formValidation(form, {
            fields: {
                password: {
                    validators: {
                        callback: {
                            callback: validatePassword
                        }
                    }
                },
                cpassword: {
                    validators: {
                        notEmpty: {
                            message: 'Confirm Password is required'
                        },
                        identical: {
                            compare: function () {
                                return form.querySelector('[name="password"]').value;
                            },
                            message: 'The password and its confirm are not the same'
                        }
                    }
                },
            },
            plugins: { //Learn more: https://formvalidation.io/guide/plugins
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // defaultSubmit: new FormValidation.plugins.DefaultSubmit(), // Uncomment this line to enable normal button submit after form validation
                bootstrap: new FormValidation.plugins.Bootstrap({
                    //	eleInvalidClass: '', // Repace with uncomment to hide bootstrap validation icons
                    eleValidClass: '',   // Repace with uncomment to hide bootstrap validation icons
                })
            }
        }).on('core.form.valid', function () {
            // Show loading state on button
            KTUtil.btnWait(formSubmitButton, _buttonSpinnerClasses, "Please wait"); // Simulate Ajax request

            // form.submit(); // Submit form
            FormValidation.utils.fetch(formSubmitUrl, {
                method: 'POST',
                dataType: 'json',
                params: {
                    csrfmiddlewaretoken: form.querySelector('[name="csrfmiddlewaretoken"]').value,
                    password: form.querySelector('[name="password"]').value,
                },
            }).then(function (response) { // Return valid JSON
                // Release button
                KTUtil.btnRelease(formSubmitButton);
                if (response.status === 200) {
                    toastr.success('Saved New Password Successfully', 'Success');
                    setTimeout(function () {
                        location.href = '/';
                    }, 1000);
                } else {
                    Swal.fire({
                        text: response.message,
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn font-weight-bold btn-light-primary"
                        }
                    }).then(function () {
                        KTUtil.scrollTop();
                    });
                }
            });
        });
    };

    // Public Functions
    return {
        init: function init() {
            _handleFormReset();
        }
    };
}();

jQuery(document).ready(function () {
    KTLogin.init();
    $('input:eq(1)').focus();

    $('.hide-password').click(function () {
        $('#password').prop('type', 'text');
        $('#cpassword').prop('type', 'text');

        $(this).hide();
        $('.show-password').show();
    });

    $('.show-password').click(function () {
        $('#password').prop('type', 'password');
        $('#cpassword').prop('type', 'password');

        $(this).hide();
        $('.hide-password').show();
    });

    $('input').keydown(function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    });

    $('#cpassword').keydown(function (event) {
        if (event.keyCode === 13) {
            $('#kt_user_reset_form_submit_button').trigger('click');
        }
    });
});
