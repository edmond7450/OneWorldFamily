"use strict";

// Class Definition
var KTLogin = function () {
    var _buttonSpinnerClasses = 'spinner spinner-right spinner-white pr-15';

    var _handleFormForgot = function _handleFormForgot() {
        var form = KTUtil.getById('kt_user_forgot_form');
        var formSubmitUrl = KTUtil.attr(form, 'action');
        var formSubmitButton = KTUtil.getById('kt_user_forgot_form_submit_button');

        if (!form) {
            return;
        }

        FormValidation.formValidation(form, {
            fields: {
                email: {
                    validators: {
                        notEmpty: {
                            message: 'Email is required'
                        },
                        emailAddress: {
                            message: 'The value is not a valid email address'
                        }
                    }
                }
            },
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                //defaultSubmit: new FormValidation.plugins.DefaultSubmit(), // Uncomment this line to enable normal button submit after form validation
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
                    email: form.querySelector('[name="email"]').value,
                },
            }).then(function (response) { // Return valid JSON
                // Release button
                KTUtil.btnRelease(formSubmitButton);
                if (response.status === 200) {
                    Swal.fire({
                        text: "We have sent the password reset instructions to your email.",
                        icon: "success",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn font-weight-bold btn-primary",
                        }
                    }).then(function () {
                        $('#otp').prop('disabled', 'disabled');
                        $('#resend_otp').prop('disabled', 'disabled');
                    });

                    KTUtil.scrollTop();
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
            _handleFormForgot();
        }
    };
}();

jQuery(document).ready(function () {
    KTLogin.init();
    $('input:eq(1)').focus()
});
