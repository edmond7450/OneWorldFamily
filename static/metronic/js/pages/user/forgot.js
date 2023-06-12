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
                    $('#kt_user_otp_form').removeClass('d-none');
                    $('#kt_user_forgot_form').addClass('d-none');
                    $('.phone_view').text(response.phone);
                    $('#otp').focus();

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

    var _handleFormOTP = function _handleFormOTP() {
        var form = KTUtil.getById('kt_user_otp_form');
        var formSubmitUrl = KTUtil.attr(form, 'action');

        if (!form) {
            return;
        }

        FormValidation.formValidation(form, {
            fields: {
                otp: {
                    validators: {
                        callback: {
                            callback: function (input) {
                                var regex = /\d{6}/;
                                if (regex.test(input.value)) {
                                    var valid = null;
                                    jQuery.ajax({
                                        type: "POST",
                                        url: '/user/forgot_check_otp/',
                                        data: {
                                            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                                            email: $('#email').val(),
                                            otp: input.value
                                        },
                                        dataType: 'json',
                                        async: false,
                                        success: function (result) {
                                            if (result.status === 200) {
                                                Swal.fire({
                                                    text: "We'll immediately send the password reset instructions to your email.",
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

                                                FormValidation.utils.fetch(formSubmitUrl, {
                                                    method: 'POST',
                                                    dataType: 'json',
                                                    params: {
                                                        csrfmiddlewaretoken: form.querySelector('[name="csrfmiddlewaretoken"]').value,
                                                        email: $('#email').val(),
                                                        otp: form.querySelector('[name="otp"]').value,
                                                    },
                                                });

                                                valid = {
                                                    valid: true,
                                                };

                                            } else {
                                                if (result.status === 501) {
                                                    $('#otp').prop('disabled', 'disabled');
                                                    $('#resend_otp').prop('disabled', 'disabled');
                                                }
                                                valid = {
                                                    valid: false,
                                                    message: result.message
                                                }
                                            }
                                        }
                                    });
                                    if (valid) {
                                        return valid;
                                    }
                                } else {
                                    return {
                                        valid: true,
                                    };
                                }
                            }
                        }
                    }
                }
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
        });
    };

    // Public Functions
    return {
        init: function init() {
            _handleFormForgot();

            _handleFormOTP();
        }
    };
}();

var btn_resend_otp = KTUtil.getById("resend_otp");
KTUtil.addEvent(btn_resend_otp, "click", function () {
    KTUtil.btnWait(btn_resend_otp, "spinner spinner-dark spinner-right pr-15", "Sending");

    $.post('/user/forgot_send_otp/', {
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
        email: $('#email').val(),
    }, function (result) {
        if (result.status === 200) {
            KTUtil.btnRelease(btn_resend_otp);
            $('#resend_otp span').removeClass('d-none');
            var remaining = parseInt($('#resend_otp span').text()) - 1;
            if (remaining > 0)
                $('#resend_otp span').text(remaining);
            else
                $('#resend_otp').addClass('d-none');
        } else {
            toastr.error(result.message, 'Error');
        }
    });
});

jQuery(document).ready(function () {
    KTLogin.init();
    $('input:eq(1)').focus()
});
