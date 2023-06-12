"use strict";

// Class Definition
var KTLogin = function () {
    var _buttonSpinnerClasses = 'spinner spinner-right spinner-white pr-15';

    var _handleFormLogin = function _handleFormLogin() {
        var form = KTUtil.getById('kt_user_login_form');
        var formSubmitUrl = KTUtil.attr(form, 'action');
        var formSubmitButton = KTUtil.getById('kt_user_login_form_submit_button');

        if (!form) {
            return;
        }

        FormValidation.formValidation(form, {
            fields: {
                email: {
                    validators: {
                        notEmpty: {
                            message: 'Email is required'
                        }
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: 'Password is required'
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
                    password: form.querySelector('[name="password"]').value,
                },
            }).then(function (result) { // Return valid JSON
                // Release button
                KTUtil.btnRelease(formSubmitButton);
                if (result.status === 200) {
                    if (result.message === 'send_phone_otp') {
                        otp_class = 'send_phone_otp';
                        $('#kt_user_login_form').addClass('d-none');
                        $('#kt_user_otp_form').removeClass('d-none');
                        $('#kt_user_otp_form .to-otp').html('<span class="phone_hidden font-size-h6 font-weight-bolder text-dark ml-1">*** *** **</span>\n' +
                            '<span class="phone_view font-size-h6 font-weight-bolder text-dark">' + result.phone + '</span>');

                        $('#otp').focus();

                        KTUtil.scrollTop();
                    } else if (result.message === 'send_email_otp') {
                        otp_class = 'send_email_otp';
                        $('#kt_user_login_form').addClass('d-none');
                        $('#kt_user_otp_form').removeClass('d-none');
                        $('#kt_user_otp_form .to-otp').html('your email');

                        $('#otp').focus();

                        KTUtil.scrollTop();
                    } else if (result.message === 'success') {
                        location.href = '/back/';
                    } else if (result.message === 'relatives_question') {
                        // alert(result.question_list)
                        var radios = '';
                        $.each(result.question_list, function (i, question) {
                            radios += '<label class="radio radio-outline radio-outline-2x radio-primary pb-1">';
                            radios += '<input type="radio" name="choose" value="' + (i + 1) + '"/><span></span>';
                            radios += question;
                            radios += '</label>';
                        });
                        radios += '<label class="radio radio-outline radio-outline-2x radio-primary pb-1">\n' +
                            '        <input type="radio" name="choose" value="0"/>\n' +
                            '        <span></span>None of these</label>';
                        $("#check_relatives_modal .radio-list").html(radios);

                        $('#check_relatives_modal').modal('show');
                    }
                } else {
                    if (result.status === 500) {
                        Swal.fire({
                            title: "Thanks for Providing Your Info",
                            text: "We'll review your info and if we can confirm it, you'll be able to request a review in the Help Center within approximately 24 hours.",
                            icon: "warning",
                            buttonsStyling: false,
                            confirmButtonText: "Done",
                            customClass: {
                                confirmButton: "btn font-weight-bold btn-primary",
                            }
                        });
                    }
                    if (result.status > 501) {
                        Swal.fire({
                            title: result.message,
                            text: "Please contact support for further details.",
                            icon: "warning",
                            buttonsStyling: false,
                            confirmButtonText: "Done",
                            customClass: {
                                confirmButton: "btn font-weight-bold btn-primary",
                            }
                        });
                    } else {
                        Swal.fire({
                            text: result.message,
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
                }
            });
        }).on('core.form.invalid', function () {
            /*Swal.fire({
                text: "Sorry, looks like there are some errors detected, please try again.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn font-weight-bold btn-light-primary"
                }
            }).then(function () {
                KTUtil.scrollTop();
            });*/
        });
    };

    var _handleFormOTP = function _handleFormLogin() {
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
                                        url: formSubmitUrl,
                                        data: {
                                            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                                            email: $('#email').val(),
                                            password: $('#password').val(),
                                            otp: input.value
                                        },
                                        dataType: 'json',
                                        async: false,
                                        success: function (result) {
                                            if (result.status === 200) {
                                                if (result.message === 'relatives_question') {
                                                    // alert(result.question_list)
                                                    var radios = '';
                                                    $.each(result.question_list, function (i, question) {
                                                        radios += '<label class="radio radio-outline radio-outline-2x radio-primary pb-1">';
                                                        radios += '<input type="radio" name="choose" value="' + (i + 1) + '"/><span></span>';
                                                        radios += question;
                                                        radios += '</label>'
                                                    });
                                                    radios += '<label class="radio radio-outline radio-outline-2x radio-primary pb-1">\n' +
                                                        '        <input type="radio" name="choose" value="0"/>\n' +
                                                        '        <span></span>None of these</label>';
                                                    $("#check_relatives_modal .radio-list").html(radios);

                                                    $('#check_relatives_modal').modal('show');
                                                } else {
                                                    location.href = '/back/';
                                                }
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
            _handleFormLogin();

            _handleFormOTP();
        }
    };
}();

var otp_class = '';
var btn_resend_otp = KTUtil.getById("resend_otp");
KTUtil.addEvent(btn_resend_otp, "click", function () {
    KTUtil.btnWait(btn_resend_otp, "spinner spinner-dark spinner-right pr-15", "Sending");

    $.post('/user/send_otp/', {
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
        email: $('#email').val(),
        password: $('#password').val(),
        otp_class: otp_class,
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
    $('input:eq(1)').focus();

    setTimeout(function () {
        $('#kt_user_login_form_submit_button').prop('disabled', false);
    }, 3000);

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

    $('#password').keydown(function (event) {
        if (event.keyCode === 13) {
            $('#kt_user_login_form_submit_button').trigger('click');
        }
    });
});
