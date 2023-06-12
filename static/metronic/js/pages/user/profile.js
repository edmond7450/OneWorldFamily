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
                add_email: {
                    validators: {
                        callback: {
                            callback: function (input) {
                                if (input.value !== '') {
                                    if (input.value === $('#email').val()) {
                                        return {
                                            valid: true,
                                        }
                                    }
                                    var regex = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                                    if (!regex.test(input.value)) {
                                        return {
                                            valid: false,
                                            message: 'Email is not valid',
                                        };
                                    } else {
                                        var valid = null;
                                        jQuery.ajax({
                                            type: "POST",
                                            url: '/user/clean/',
                                            data: {
                                                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                                                email: input.value
                                            },
                                            dataType: 'json',
                                            async: false,
                                            success: function (result) {
                                                if (result.status === 200) {
                                                    valid = {
                                                        valid: true,
                                                    }
                                                } else {
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
                                    }
                                } else {
                                    return {
                                        valid: false,
                                        message: 'Email is required',
                                    };
                                }
                            }
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
                bootstrap: new FormValidation.plugins.Bootstrap({
                    //	eleInvalidClass: '', // Repace with uncomment to hide bootstrap validation icons
                    eleValidClass: '',   // Repace with uncomment to hide bootstrap validation icons
                })
            }
        });

        $('#profile_modal .btn-primary').click(function () {
            validation.validate().then(function (status) {
                if (status === 'Valid') {
                    var myform = $('#kt_personal_information_form');
                    var disabled = myform.find(':input:disabled').removeAttr('disabled');
                    var form_data = new FormData(myform[0]);
                    disabled.attr('disabled', 'disabled');

                    $.ajax({
                        type: 'PUT',
                        url: '/user/profile/',
                        data: form_data,
                        processData: false,
                        contentType: false,
                        headers: {
                            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
                        },
                        success: function (result) {
                            if (result.status === 200) {
                                toastr.success(result.message, 'Success');
                                $('#profile_modal').modal('hide');
                                var data_index = datatable.originalDataSet.findIndex(x => x.id === result.data.id);
                                datatable.originalDataSet[data_index]['avatar'] = result.data.avatar;
                                datatable.originalDataSet[data_index]['name'] = result.data.name;
                                datatable.originalDataSet[data_index]['username'] = result.data.username;
                                datatable.originalDataSet[data_index]['phone'] = result.data.phone;
                                datatable.originalDataSet[data_index]['last_login'] = result.data.last_login;
                                datatable.originalDataSet[data_index]['city'] = result.data.city;
                                datatable.originalDataSet[data_index]['state'] = result.data.state;
                                datatable.originalDataSet[data_index]['membership_date'] = result.data.membership_date;

                                datatable.reload()
                            } else {
                                toastr.error(result.message, 'Error');
                            }
                        }
                    });
                }
            });
        });

        form.querySelector('[name="address"]').addEventListener('input', function (e) {
            $('#postal_code').val('');
        });
    };

    // Public Functions
    return {
        init: function init() {
            _initAside();

            _handleFormPersonalInfomation();
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

    $('input').keydown(function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    });
});

function edit_user(user_id) {
    $.ajax({
        url: '/user/profile/',
        type: 'GET',
        data: {
            'id': user_id
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (result) {
            if (result.status === 200) {
                $('#kt_personal_information_form')[0].reset();
                validation.resetForm();

                if (result.data.avatar) {
                    $('#kt_profile_avatar').removeClass('image-input-empty');
                    $('#kt_profile_avatar .image-input-wrapper').css('background-image', 'url(' + result.data.avatar + ')');
                } else {
                    $('#kt_profile_avatar').addClass('image-input-empty');
                    $('#kt_profile_avatar .image-input-wrapper').css('background-image', '');
                }
                var avatar = new KTImageInput('kt_profile_avatar');

                $('#user_id').val(user_id);
                $('#first_name').val(result.data.first_name);
                $('#last_name').val(result.data.last_name);
                $('#email').val(result.data.email);
                $('#add_email').val(result.data.email);
                $('#phone').val(result.data.phone);
                $('#birthday').datepicker('setDate', result.data.birthday);

                $('#profile_modal input[type="radio"][value="' + result.data.gender + '"]').prop('checked', true);

                $('#address').val(result.data.address);
                $('#postal_code').val(result.data.postal_code);

                $('#profile_modal .btn-primary').text('Save');
                $('#profile_modal').modal('show');

            } else {
                toastr.error(result.message, 'Error');
            }
        }
    });
}