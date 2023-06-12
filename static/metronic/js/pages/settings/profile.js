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
var validation = null;
var KTSettings = function () {
    var avatar;
    var offcanvas;
    var _buttonSpinnerClasses = 'spinner spinner-right spinner-white pr-15';

    // Private functions
    var _initAside = function _initAside() {
        // Mobile offcanvas for mobile mode
        offcanvas = new KTOffcanvas('kt_profile_aside', {
            overlay: true,
            baseClass: 'offcanvas-mobile',
            //closeBy: 'kt_user_profile_aside_close',
            toggleBy: 'kt_subheader_mobile_toggle'
        });
    };

    var _handleFormPersonalInfomation = function _handleFormPersonalInfomation() {
        var form = KTUtil.getById('kt_personal_information_form');
        var formSubmitButton = KTUtil.getById('kt_personal_information_form_submit_button');

        if (!form) {
            return;
        }

        avatar = new KTImageInput('kt_profile_avatar');

        validation = FormValidation.formValidation(form, {
            fields: {
                first_name: {
                    validators: {
                        notEmpty: {
                            message: 'First Name is required'
                        },
                        regexp: {
                            regexp: '^[A-Z][a-z]+$',
                            message: 'First Name is not a valid',
                        }
                    }
                },
                last_name: {
                    validators: {
                        notEmpty: {
                            message: 'Last Name is required'
                        },
                        regexp: {
                            regexp: '^[A-Z][a-z]+$',
                            message: 'Last Name is not a valid',
                        }
                    }
                },
                phone: {
                    validators: {
                        notEmpty: {
                            message: 'Mobile phone number is required'
                        },
                        phone: {
                            country: 'US',
                            message: 'The value is not a valid Mobile phone number'
                        }
                    }
                },
                birthday: {
                    validators: {
                        notEmpty: {
                            message: 'Birthday is required'
                        }
                    }
                },
                gender: {
                    validators: {
                        notEmpty: {
                            message: 'Please select an option'
                        }
                    }
                },
                address: {
                    validators: {
                        callback: {
                            callback: function (input) {
                                if (input.value === '') {
                                    return {
                                        valid: false,
                                        message: 'Address is required'
                                    }
                                }
                                var addresses = input.value.split(', ');
                                if (addresses.length < 4 || addresses.length > 5) {
                                    return {
                                        valid: false,
                                        message: 'The address format is not correct.'
                                    }
                                }
                                return {
                                    valid: true
                                }
                            }
                        }
                    }
                },
                postal_code: {
                    validators: {
                        notEmpty: {
                            message: 'Zip Code is required'
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

            var myform = $('#kt_personal_information_form');
            var disabled = myform.find(':input:disabled').removeAttr('disabled');
            form.submit(); // Submit form
            disabled.attr('disabled', 'disabled');
        });

        form.querySelector('[name="address"]').addEventListener('input', function (e) {
            $('#postal_code').val('');
        });
    };

    var _handleFormChangePassword = function _handleFormChangePassword() {
        var form = KTUtil.getById('kt_change_password_form');
        var formSubmitButton = KTUtil.getById('kt_change_password_form_submit_button');

        if (!form) {
            return;
        }

        FormValidation.formValidation(form, {
            fields: {
                current_password: {
                    validators: {
                        notEmpty: {
                            message: 'Current Password is required'
                        }
                    }
                },
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

            form.submit(); // Submit form
        });
    };

    // Public Functions
    return {
        init: function init() {
            _initAside();

            _handleFormPersonalInfomation();

            _handleFormChangePassword();
        }
    };
}();

jQuery(document).ready(function () {
    KTSettings.init();
    $('.datepicker').datepicker({
        format: 'MM d, yyyy',
        autoclose: true,
        orientation: "bottom"
    });
    $('input:eq(1)').focus();

    $('input').keydown(function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    });

    $('#kt_profile_aside .navi-link').click(function () {
        $('#kt_profile_aside .navi-link').removeClass('active');
        $(this).addClass('active');

        $('.profile-form').addClass('d-none');

        var classes = $(this).attr('class');
        if (classes.indexOf('profile-overview') >= 0) {
            $('#kt_profile_overview_form').removeClass('d-none');
        } else if (classes.indexOf('personal-information') >= 0) {
            $('#kt_personal_information_form').removeClass('d-none');
        } else if (classes.indexOf('change-password') >= 0) {
            $('#kt_change_password_form').removeClass('d-none');
        } else if (classes.indexOf('account-security') >= 0) {
            $('#kt_account_security_form').removeClass('d-none');
        } else if (classes.indexOf('social-profile') >= 0) {
            $('#kt_social_profile_form').removeClass('d-none');
        }
    });
    if (request_class) {
        $("." + request_class).trigger('click');
    }

    // Change Password
    $('.hide-password').click(function () {
        $('#current_password').prop('type', 'text');
        $('#password').prop('type', 'text');
        $('#cpassword').prop('type', 'text');

        $(this).hide();
        $('.show-password').show();
    });

    $('.show-password').click(function () {
        $('#current_password').prop('type', 'password');
        $('#password').prop('type', 'password');
        $('#cpassword').prop('type', 'password');

        $(this).hide();
        $('.hide-password').show();
    });

    // Account Security
    $('.save-two-factor-methond').click(function () {
        var two_factor = parseInt($('input[name="two_factor"]:checked').val());
        var two_factor_text = $('.two-factor-method').text();
        if (two_factor === 1 && two_factor_text === 'SMS' || two_factor === 2 && two_factor_text === 'email') {
            $('#two_factor_method_modal').modal('hide');
            return;
        }

        var btn_save = this;
        KTUtil.btnWait(btn_save, "spinner spinner-right pr-15", "Saving");

        $.post('/back/settings/profile/change_two_factor/', {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            two_factor: two_factor,
        }, function (result) {
            KTUtil.btnRelease(btn_save);

            if (result.status === 200) {
                toastr.success('Saved Successfully', 'Success');

                if (two_factor === 1) {
                    $('.two-factor-method').text('SMS');
                } else if (two_factor === 2) {
                    $('.two-factor-method').text('email');
                }
                $('#two_factor_method_modal').modal('hide');

            } else {
                toastr.error(result.message, 'Error');
            }
        });
    });

    $('.edit-personal-information').click(function () {
        $('#two_factor_confirm_modal').modal('hide');
        $('.personal-information').trigger('click');
    });

    $(".turn-off-two-factor").click(function (e) {
        Swal.fire({
            title: "Turn off two-factor authentication",
            text: "Turning off two-factor authentication will leave your account less secure and more vulnerable. Are you sure you wish to continue?",
            width: 600,
            showCancelButton: true,
            confirmButtonText: "Yes, turn off!",
            cancelButtonText: "No, cancel!",
            reverseButtons: true
        }).then(function (result) {
            if (result.value) {
                $.post('/back/settings/profile/change_two_factor/', {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    two_factor: 0,
                }, function (result) {
                    if (result.status === 200) {
                        Swal.fire({
                            title: "Two factor authentication deactivated",
                            text: "Two-factor authentication has now been deactivated on your account.",
                            width: 600,
                            icon: "warning",
                            confirmButtonText: "Confirm me!",
                        });
                        $('.two-factor-on').addClass('d-none');
                        $('.two-factor-off').removeClass('d-none');
                    } else {
                        toastr.error(result.message, 'Error');
                    }
                });
            }
        });
    });

    $(".turn-on-two-factor").click(function (e) {
        $.post('/back/settings/profile/change_two_factor/', {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            two_factor: 1,
        }, function (result) {
            $('#two_factor_confirm_modal').modal('hide');

            if (result.status === 200) {
                Swal.fire({
                    title: "Two factor authentication activated",
                    text: "Congratulations! Two-factor authentication has now been activated on your account.",
                    width: 600,
                    icon: "success",
                    confirmButtonText: "OK",
                });
                $('.two-factor-off').addClass('d-none');
                $('.two-factor-on').removeClass('d-none');
            } else {
                toastr.error(result.message, 'Error');
            }
        });
    });

});