var datatable;

var KTDatatableRemoteAjax = function () {
    // initializer
    var init = function () {
        var actions_title = '';
        var actions_width = 0;
        if (is_update === true && is_delete === true) {
            actions_title = 'Actions';
            actions_width = 100;
        } else if (is_update === true || is_delete === true) {
            actions_title = 'Action';
            actions_width = 55;
        }
        var columns = [
            {
                field: 'id',
                title: '',
                sortable: false,
                width: 20,
                selector: {
                    class: ''
                }
            }, {
                field: 'ID',
                title: 'id',
                width: 40,
                type: 'number',
                textAlign: 'left',
                template: function (row) {
                    return '<span class="font-weight-bolder">' + row.id + '</span>';
                }
            }, {
                field: 'name',
                title: 'Name',
                width: 300,
                overflow: 'visible',
                template: function (row) {
                    var output = '';
                    if (row.avatar) {
                        output = '<div class="d-flex align-items-center">\
                            <div class="symbol symbol-40 symbol-sm flex-shrink-0">\
                                <img class="w-40px" src="' + row.avatar + '" alt="photo">\
                            </div>\
                            <div class="ml-4">\
                                <div class="text-dark-75 font-weight-bolder font-size-lg mb-0">' + row.name + '</div>\
                                <div class="text-muted">' + row.username + '</div>\
                            </div>\
                        </div>';
                    } else {
                        var stateNo = KTUtil.getRandomInt(0, 7);
                        var states = ['success', 'primary', 'danger', 'success', 'warning', 'dark', 'primary', 'info'];
                        var state = states[stateNo];

                        output = '<div class="d-flex align-items-center">\
                            <div class="symbol symbol-40 symbol-light-' + state + ' flex-shrink-0">\
                                <span class="symbol-label font-size-h4 font-weight-bold">' + row.name.substring(0, 1) + '</span>\
                            </div>\
                            <div class="ml-4">\
                                <div class="text-dark-75 font-weight-bolder font-size-lg mb-0">' + row.name + '</div>\
                                <div class="text-muted">' + row.username + '</div>\
                            </div>\
                        </div>';
                    }
                    return output;
                },
            }, {
                field: 'business_name',
                title: 'Business Name',
                width: 120,
                template: function (row) {
                    return '<div class="font-weight-bolder font-size-lg mb-0 text-nowrap">' + row.business_name + '</div>' +
                        '<div class="text-muted text-nowrap">' + row.phone + '</div>';
                }
            }, {
                field: 'last_login',
                title: 'Login Date',
                width: 90,
                type: 'date',
                format: 'MM/DD/YYYY',
                template: function (row) {
                    return '<div class="font-weight-bolder text-primary mb-0">' + row.last_login + '</div>' +
                        '<div class="text-muted">' + row.date_joined + '</div>';
                },
            }, {
                field: 'membership_date',
                title: 'Billing Date',
                width: 100,
                type: 'date',
                format: 'MM/DD/YYYY',
                template: function (row) {
                    var output = '<div class="font-weight-bolder font-size-lg mb-0 text-nowrap">' + row.membership_date + '</div>';
                    if (row.close_account_info)
                        output += '<div class="text-danger">' + row.close_account_info + '</div>';
                    return output;
                },
            }, {
                field: 'feeds',
                title: 'Feeds',
                sortable: false,
                width: 45,
                type: 'number',
                textAlign: 'right',
                template: function (row) {
                    if (row.feeds)
                        return '<span class="font-weight-bolder">' + row.feeds + '</span>';
                    else
                        return '';
                }
            }, {
                field: 'status',
                title: 'Status',
                width: 90,
                overflow: 'visible',
                template: function (row) {
                    var status = {
                        1: {'title': 'Verified', 'class': 'label-success'},
                        0: {'title': 'Inactive', 'class': 'label-light'},
                        2: {'title': 'Internal User', 'class': 'label-light-success'},
                        3: {'title': 'Security Checking', 'class': 'label-light-info'},
                        4: {'title': 'Restricted', 'class': 'label-light-warning'},
                        5: {'title': 'Closed', 'class': 'label-light-danger'},
                    };
                    return '<span class="label label-lg font-weight-bold ' + status[row.status].class + ' label-inline text-nowrap">' + status[row.status].title + '</span>';
                }
            }, {
                field: 'size',
                title: 'size',
                width: 60,
                template: function (row) {
                    var output = '';
                    output += '<div>' + row.size + '</div>';
                    output += '<div>' + row.s3_size + '</div>';
                    return output;
                },
            }, {
                field: 'owner',
                title: 'owner',
                width: 50,
                type: 'number',
            }, {
                field: 'actions',
                title: actions_title,
                sortable: false,
                width: actions_width,
                overflow: 'visible',
                autoHide: false,
                template: function (row) {
                    var output = '';
                    if (is_update === true) {
                        output += '<button class="btn-actions mr-2" onclick="edit_user(' + row.id + ')" title="Edit details">' +
                            '<span><svg viewBox="0 0 512 511" width="14px" height="14px" xmlns="http://www.w3.org/2000/svg"><path d="m405.332031 256.484375c-11.796875 0-21.332031 9.558594-21.332031 21.332031v170.667969c0 11.753906-9.558594 21.332031-21.332031 21.332031h-298.667969c-11.777344 0-21.332031-9.578125-21.332031-21.332031v-298.667969c0-11.753906 9.554687-21.332031 21.332031-21.332031h170.667969c11.796875 0 21.332031-9.558594 21.332031-21.332031 0-11.777344-9.535156-21.335938-21.332031-21.335938h-170.667969c-35.285156 0-64 28.714844-64 64v298.667969c0 35.285156 28.714844 64 64 64h298.667969c35.285156 0 64-28.714844 64-64v-170.667969c0-11.796875-9.539063-21.332031-21.335938-21.332031zm0 0"/><path d="m200.019531 237.050781c-1.492187 1.492188-2.496093 3.390625-2.921875 5.4375l-15.082031 75.4375c-.703125 3.496094.40625 7.101563 2.921875 9.640625 2.027344 2.027344 4.757812 3.113282 7.554688 3.113282.679687 0 1.386718-.0625 2.089843-.210938l75.414063-15.082031c2.089844-.429688 3.988281-1.429688 5.460937-2.925781l168.789063-168.789063-75.414063-75.410156zm0 0"/><path d="m496.382812 16.101562c-20.796874-20.800781-54.632812-20.800781-75.414062 0l-29.523438 29.523438 75.414063 75.414062 29.523437-29.527343c10.070313-10.046875 15.617188-23.445313 15.617188-37.695313s-5.546875-27.648437-15.617188-37.714844zm0 0"/></svg></span>' +
                            '</button>';
                    }
                    if (is_delete === true) {
                        if (row.status !== 5)
                            output += '<button class="btn-actions" onclick="close_user(' + row.id + ')" title="Close">' +
                                '<span>' +
                                '    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="14px" height="14px" viewBox="0 0 24 24" version="1.1">' +
                                '        <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">' +
                                '            <rect x="0" y="0" width="24" height="24"/>' +
                                '            <path d="M12,22 C6.4771525,22 2,17.5228475 2,12 C2,6.4771525 6.4771525,2 12,2 C17.5228475,2 22,6.4771525 22,12 C22,17.5228475 17.5228475,22 12,22 Z M12,20 C16.418278,20 20,16.418278 20,12 C20,7.581722 16.418278,4 12,4 C7.581722,4 4,7.581722 4,12 C4,16.418278 7.581722,20 12,20 Z M19.0710678,4.92893219 L19.0710678,4.92893219 C19.4615921,5.31945648 19.4615921,5.95262146 19.0710678,6.34314575 L6.34314575,19.0710678 C5.95262146,19.4615921 5.31945648,19.4615921 4.92893219,19.0710678 L4.92893219,19.0710678 C4.5384079,18.6805435 4.5384079,18.0473785 4.92893219,17.6568542 L17.6568542,4.92893219 C18.0473785,4.5384079 18.6805435,4.5384079 19.0710678,4.92893219 Z" fill="#000000" fill-rule="nonzero" opacity="0.3"/>' +
                                '        </g>' +
                                '    </svg>' +
                                '</span>' +
                                '</button>';
                        else
                            output += '<button class="btn-actions" onclick="delete_user(' + row.id + ')" title="Delete">' +
                                '<span>' +
                                '    <svg viewBox="-40 0 427 427.00131" width="14px" height="14px" xmlns="http://www.w3.org/2000/svg">' +
                                '        <path d="m232.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/>' +
                                '        <path d="m114.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/>' +
                                '        <path d="m28.398438 127.121094v246.378906c0 14.5625 5.339843 28.238281 14.667968 38.050781 9.285156 9.839844 22.207032 15.425781 35.730469 15.449219h189.203125c13.527344-.023438 26.449219-5.609375 35.730469-15.449219 9.328125-9.8125 14.667969-23.488281 14.667969-38.050781v-246.378906c18.542968-4.921875 30.558593-22.835938 28.078124-41.863282-2.484374-19.023437-18.691406-33.253906-37.878906-33.257812h-51.199218v-12.5c.058593-10.511719-4.097657-20.605469-11.539063-28.03125-7.441406-7.421875-17.550781-11.5546875-28.0625-11.46875h-88.796875c-10.511719-.0859375-20.621094 4.046875-28.0625 11.46875-7.441406 7.425781-11.597656 17.519531-11.539062 28.03125v12.5h-51.199219c-19.1875.003906-35.394531 14.234375-37.878907 33.257812-2.480468 19.027344 9.535157 36.941407 28.078126 41.863282zm239.601562 279.878906h-189.203125c-17.097656 0-30.398437-14.6875-30.398437-33.5v-245.5h250v245.5c0 18.8125-13.300782 33.5-30.398438 33.5zm-158.601562-367.5c-.066407-5.207031 1.980468-10.21875 5.675781-13.894531 3.691406-3.675781 8.714843-5.695313 13.925781-5.605469h88.796875c5.210937-.089844 10.234375 1.929688 13.925781 5.605469 3.695313 3.671875 5.742188 8.6875 5.675782 13.894531v12.5h-128zm-71.199219 32.5h270.398437c9.941406 0 18 8.058594 18 18s-8.058594 18-18 18h-270.398437c-9.941407 0-18-8.058594-18-18s8.058593-18 18-18zm0 0"/>' +
                                '        <path d="m173.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/>' +
                                '    </svg>' +
                                '</span>' +
                                '</button>';
                    }
                    return output;
                }
            }];

        datatable = $('#kt_datatable').KTDatatable({
            // enable extension
            /*extensions: {
                // boolean or object (extension options)
                checkbox: true,
            },*/

            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        url: '/user/client/list/',
                        params: {
                            csrfmiddlewaretoken: csrf_token
                        },
                        // sample custom headers
                        // headers: {'x-my-custom-header': 'some value', 'x-test-header': 'the value'},
                        map: function (raw) {
                            // sample data mapping
                            var dataSet = null;
                            if (typeof raw.users !== 'undefined') {
                                dataSet = raw.users;
                            }
                            return dataSet;
                        },
                    },
                },
                pageSize: 10,
                serverPaging: true,
                serverFiltering: true,
                serverSorting: true,
            },

            // layout definition
            layout: {
                scroll: false,
                footer: false,
            },

            // column sorting
            sortable: true,

            pagination: true,

            search: {
                input: $('#kt_datatable_search_query'),
                key: 'generalSearch'
            },

            // columns definition
            columns: columns,
        });

        $('#kt_datatable_show_only_owner').on('change', function () {
            datatable.search($(this).prop('checked').toString(), 'show_only_owner');

            $('#kt_datatable_group_action_form').collapse('hide');
        });

        $('#kt_datatable_search_status').on('change', function () {
            datatable.search($(this).val(), 'status');

            $('#kt_datatable_group_action_form').collapse('hide');
        });

        $("#kt_last_login_datepicker input:eq(0)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_last_login_datepicker input:eq(1)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['to_last_login'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'from_last_login');
        });

        $("#kt_last_login_datepicker input:eq(1)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_last_login_datepicker input:eq(0)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['from_last_login'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'to_last_login');
        });

        $("#kt_membership_date_datepicker input:eq(0)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_membership_date_datepicker input:eq(1)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['to_membership_date'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'from_membership_date');
        });

        $("#kt_membership_date_datepicker input:eq(1)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_membership_date_datepicker input:eq(0)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['from_membership_date'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'to_membership_date');
        });

        datatable.on(
            'datatable-on-check datatable-on-uncheck',
            function (e) {
                var checkedNodes = datatable.rows('.datatable-row-active').nodes();
                var count = checkedNodes.length;
                $('#kt_datatable_selected_records').html(count);
                if ($('#kt_datatable_search_status').val() === '5') {
                    $('#kt_datatable_close_selected').addClass('d-none');
                    $('#kt_datatable_delete_selected').removeClass('d-none');
                } else {
                    $('#kt_datatable_close_selected').removeClass('d-none');
                    $('#kt_datatable_delete_selected').addClass('d-none');
                }
                if (count > 0) {
                    $('#kt_datatable_group_action_form').collapse('show');
                } else {
                    $('#kt_datatable_group_action_form').collapse('hide');
                }
            });
    };

    return {
        // Public functions
        init: function () {
            init();
        },
    };
}();

jQuery(document).ready(function () {
    KTDatatableRemoteAjax.init();

    $('#kt_last_login_datepicker, #kt_membership_date_datepicker').datepicker({
        format: 'mm/dd/yyyy',
        todayHighlight: true,
        autoclose: true,
        orientation: 'bottom'
    });

    $('#kt_datatable_search_status').selectpicker();
});


function close_user(id) {
    Swal.fire({
        title: "Confirm Close User Account",
        text: "Are you sure you want to close this user account?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, close it!",
        cancelButtonText: "No, cancel!"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: '/user/client/list/',
                type: 'PUT',
                data: {
                    'id': id
                },
                dataType: 'json',
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (result) {
                    if (result.status === 200) {
                        datatable.reload();
                        toastr.success(result.message, 'Success');
                    } else {
                        toastr.error(result.message, 'Error');
                    }
                }
            });
        }
    });
}

function close_users() {
    if ($('#kt_datatable_search_status').val() === '5') return;

    var ids = datatable.rows('.datatable-row-active').nodes().find('.checkbox > [type="checkbox"]').map(function (i, chk) {
        return $(chk).val();
    });
    if (ids.length === 0)
        return;

    Swal.fire({
        title: "Confirm Close User Account",
        text: "Are you sure you want to close the selected " + ids.length + " user(s)?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, close!",
        cancelButtonText: "No, cancel!"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: '/user/client/list/',
                type: 'PUT',
                data: {
                    'ids': ids.toArray()
                },
                dataType: 'json',
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (result) {
                    if (result.status === 200) {
                        $('#kt_datatable_group_action_form').collapse('hide');
                        datatable.reload();
                        toastr.success(result.message, 'Success');
                    } else {
                        toastr.error(result.message, 'Error');
                    }
                }
            });
        }
    });
}

function delete_user(id) {
    Swal.fire({
        title: "Confirm Delete User",
        text: "Are you sure you want to permanently delete this user?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "No, cancel!"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: '/user/client/list/',
                type: 'DELETE',
                data: {
                    'id': id
                },
                dataType: 'json',
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (result) {
                    if (result.status === 200) {
                        datatable.reload();
                        toastr.success(result.message, 'Success');
                    } else {
                        toastr.error(result.message, 'Error');
                    }
                }
            });
        }
    });
}

function delete_users() {
    if ($('#kt_datatable_search_status').val() !== '5') return;

    var ids = datatable.rows('.datatable-row-active').nodes().find('.checkbox > [type="checkbox"]').map(function (i, chk) {
        return $(chk).val();
    });
    if (ids.length === 0)
        return;

    Swal.fire({
        title: "Confirm Delete User",
        text: "Are you sure you want to permanently delete the selected " + ids.length + " user(s)?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, delete!",
        cancelButtonText: "No, cancel!"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: '/user/client/list/',
                type: 'DELETE',
                data: {
                    'ids': ids.toArray()
                },
                dataType: 'json',
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (result) {
                    if (result.status === 200) {
                        $('#kt_datatable_group_action_form').collapse('hide');
                        datatable.reload();
                        toastr.success(result.message, 'Success');
                    } else {
                        toastr.error(result.message, 'Error');
                    }
                }
            });
        }
    });
}
