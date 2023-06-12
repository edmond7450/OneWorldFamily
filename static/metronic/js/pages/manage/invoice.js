var datatable;

var KTDatatableRemoteAjax = function () {
    // initializer
    var init = function () {
        var columns = [
            {
                field: 'index',
                title: '#',
                width: 40,
                type: 'number',
                selector: false,
                textAlign: 'left'
            }, {
                field: 'invoice_number',
                title: 'Invoice Number',
                width: 180,
            }/*, {
                field: 'subtotal',
                title: 'Subtotal',
                width: 60,
                type: 'number',
                textAlign: 'right'
            }, {
                field: 'tax',
                title: 'Tax',
                width: 60,
                type: 'number',
                textAlign: 'right'
            }*/, {
                field: 'total',
                title: 'Total',
                width: 60,
                type: 'number',
                textAlign: 'right'
            }, {
                field: 'created_at',
                title: 'Date',
                width: 100,
                type: 'date',
                format: 'MM/DD/YYYY',
            }, {
                field: 'username',
                title: 'User',
                width: 300,
                autoHide: false,
                template: function (row) {
                    return '<div class="text-nowrap" >' + row.username + '</div>';
                },
            }, {
                field: 'actions',
                title: 'Actions',
                sortable: false,
                width: 70,
                overflow: 'visible',
                autoHide: false,
                template: function (row) {
                    return '<button class="btn-actions mr-2" onclick="window.open(\'/back/manage/invoice/?id=' + row.id + '\', \'_self\')" title="Download">' +
                        '<span><svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z" class=""></path></svg></span>' +
                        '</button>';
                }
            }];

        datatable = $('#kt_datatable').KTDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        url: '/back/manage/invoice/',
                        params: {
                            csrfmiddlewaretoken: csrf_token
                        },
                        // sample custom headers
                        // headers: {'x-my-custom-header': 'some value', 'x-test-header': 'the value'},
                        map: function (raw) {
                            // sample data mapping
                            var dataSet = null;
                            if (typeof raw.items !== 'undefined') {
                                dataSet = raw.items;
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

        $("#kt_datepicker input:eq(0)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_datepicker input:eq(1)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['to_date'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'from_date');
        });

        $("#kt_datepicker input:eq(1)").on('change', function () {
            var query = datatable.getDataSourceQuery();
            var date = $("#kt_datepicker input:eq(0)").val();
            var dates;
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            query['from_date'] = date;
            datatable.setDataSourceQuery(query);

            date = $(this).val();
            if (date.indexOf('/') > 0) { // MM/DD/YYYY => YYYY-MM-DD
                dates = date.split('/');
                date = dates[2] + '-' + dates[0] + '-' + dates[1]
            }
            datatable.search(date, 'to_date');
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

    $('#kt_datepicker').datepicker({
        format: 'mm/dd/yyyy',
        todayHighlight: true,
        autoclose: true,
        orientation: 'bottom'
    });

    options = '<option value="">All</option>';
    $.each(users, function (i, user) {
        if (!user.is_active)
            options += '<option value="' + user.id + '">' + user.username + ' (inactive)</option>';
        else
            options += '<option value="' + user.id + '">' + user.username + '</option>';
    });
    $('#kt_datatable_search_user').html(options).select2().on('change', function () {
        datatable.search($(this).val(), 'user_id');
    });
    $('#kt_datatable_search_user').parent().find('.select2').addClass('w-100');
});
