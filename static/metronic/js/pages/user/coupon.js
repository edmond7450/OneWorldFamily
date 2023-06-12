var datatable;

var KTDatatableRemoteAjax = function () {
    // initializer
    var init = function () {
        var columns = [
            {
                field: 'id',
                title: 'id',
                width: 0,
                visible: false
            }, {
                field: 'index',
                title: '#',
                width: 40,
                type: 'number',
                selector: false,
                textAlign: 'left',
                template: function (row) {
                    return '<span class="font-weight-bolder">' + row.index + '</span>';
                }
            }, {
                field: 'coupon_code',
                title: 'Coupon Code',
                width: 150,
                overflow: 'visible',
                template: function (row) {
                    return '<div class="font-weight-bolder font-size-lg mb-0 text-nowrap">' + row.coupon_code + '</div>';
                }
            }, {
                field: 'months',
                title: 'Months',
                width: 60
            }, {
                field: 'started_at',
                title: 'Start Date',
                type: 'date',
                format: 'MM/DD/YYYY',
                template: function (row) {
                    return '<div class="font-weight-bolder font-size-lg mb-0 text-nowrap">' + row.started_at + '</div>';
                },
            }, {
                field: 'username',
                title: 'User',
                width: 200,
                overflow: 'visible',
                template: function (row) {
                    return '<div class="text-nowrap" >' + row.username + '</div>';
                },
            }, {
                field: 'actions',
                title: 'Actions',
                sortable: false,
                width: 70,
                overflow: 'visible',
                template: function (row) {
                    var output = '';
                    if (row.started_at === '')
                        output += '<button class="btn-actions" onclick="delete_coupon(' + row.id + ')" title="Delete">' +
                            '<span><svg height="14px" viewBox="-40 0 427 427.00131" width="14px" xmlns="http://www.w3.org/2000/svg"><path d="m232.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/><path d="m114.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/><path d="m28.398438 127.121094v246.378906c0 14.5625 5.339843 28.238281 14.667968 38.050781 9.285156 9.839844 22.207032 15.425781 35.730469 15.449219h189.203125c13.527344-.023438 26.449219-5.609375 35.730469-15.449219 9.328125-9.8125 14.667969-23.488281 14.667969-38.050781v-246.378906c18.542968-4.921875 30.558593-22.835938 28.078124-41.863282-2.484374-19.023437-18.691406-33.253906-37.878906-33.257812h-51.199218v-12.5c.058593-10.511719-4.097657-20.605469-11.539063-28.03125-7.441406-7.421875-17.550781-11.5546875-28.0625-11.46875h-88.796875c-10.511719-.0859375-20.621094 4.046875-28.0625 11.46875-7.441406 7.425781-11.597656 17.519531-11.539062 28.03125v12.5h-51.199219c-19.1875.003906-35.394531 14.234375-37.878907 33.257812-2.480468 19.027344 9.535157 36.941407 28.078126 41.863282zm239.601562 279.878906h-189.203125c-17.097656 0-30.398437-14.6875-30.398437-33.5v-245.5h250v245.5c0 18.8125-13.300782 33.5-30.398438 33.5zm-158.601562-367.5c-.066407-5.207031 1.980468-10.21875 5.675781-13.894531 3.691406-3.675781 8.714843-5.695313 13.925781-5.605469h88.796875c5.210937-.089844 10.234375 1.929688 13.925781 5.605469 3.695313 3.671875 5.742188 8.6875 5.675782 13.894531v12.5h-128zm-71.199219 32.5h270.398437c9.941406 0 18 8.058594 18 18s-8.058594 18-18 18h-270.398437c-9.941407 0-18-8.058594-18-18s8.058593-18 18-18zm0 0"/><path d="m173.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/></svg></span>' +
                            '</button>';
                    return output;
                }
            }];

        datatable = $('#kt_datatable').KTDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        url: '/user/coupon/',
                        params: {
                            csrfmiddlewaretoken: csrf_token
                        },
                        // sample custom headers
                        // headers: {'x-my-custom-header': 'some value', 'x-test-header': 'the value'},
                        map: function (raw) {
                            // sample data mapping
                            var dataSet = null;
                            if (typeof raw.coupons !== 'undefined') {
                                dataSet = raw.coupons;
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

        $('#kt_datatable_search_status').on('change', function () {
            datatable.search($(this).val().toLowerCase(), 'status');
        });

        $("#kt_started_at_datepicker input:eq(0)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_started_at_datepicker input:eq(1)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['to_started_at'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'from_started_at');
        });

        $("#kt_started_at_datepicker input:eq(1)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_started_at_datepicker input:eq(0)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['from_started_at'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'to_started_at');
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

    $('#kt_started_at_datepicker').datepicker({
        format: 'mm/dd/yyyy',
        todayHighlight: true,
        autoclose: true,
        orientation: 'bottom'
    });

    $('#kt_datatable_search_status').selectpicker();
});

$('.new-coupon').click(function () {
    var btn_add = this;
    KTUtil.btnWait(btn_add, "spinner spinner-right pr-15", "Creating");

    $.ajax({
        type: 'PUT',
        url: '/user/coupon/',
        data: {
            'months': 1
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (result) {
            KTUtil.btnRelease(btn_add);

            if (result.status === 200) {
                datatable.reload();
                toastr.success(result.coupon_code, 'Success');
            } else {
                toastr.error(result.message, 'Error');
            }
        }
    });
});

$('.new-order').click(function () {
    var btn_add = this;
    KTUtil.btnWait(btn_add, "spinner spinner-right pr-15", "Creating");

    $.ajax({
        type: 'PUT',
        url: '/user/coupon/',
        data: {
            'months': -1
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (result) {
            KTUtil.btnRelease(btn_add);

            if (result.status === 200) {
                datatable.reload();
                toastr.success(result.coupon_code, 'Success');
            } else {
                toastr.error(result.message, 'Error');
            }
        }
    });
});

function delete_coupon(id) {
    Swal.fire({
        title: "Confirm Delete Row",
        text: "Are you sure you want to delete this row?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "No, cancel!"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: '/user/coupon/',
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