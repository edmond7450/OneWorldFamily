var datatable;

var KTDatatableRemoteAjax = function () {
    // initializer
    var init = function () {
        var columns = [
            {
                field: 'user_id',
                title: 'user_id',
                width: 0,
                visible: false,
            }, {
                field: 'index',
                title: '#',
                width: 40,
                type: 'number',
                selector: false,
                textAlign: 'left'
            }, {
                field: 'category',
                title: 'Category',
                width: 120,
            }, {
                field: 'action',
                title: 'Action',
            }, {
                field: 'comment',
                title: 'Comment',
            }, {
                field: 'created_at',
                title: 'Date',
                width: 100,
                type: 'date',
                format: 'MM/DD/YYYY',
            }, {
                field: 'username',
                title: 'User',
                overflow: 'visible',
                template: function (row) {
                    return '<div class="text-nowrap" >' + row.username + '</div>';
                },
            }];

        datatable = $('#kt_datatable').KTDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        url: '/back/manage/history/',
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

    var options = '<option value="">All</option>';
    $.each(categories, function (i, category) {
        options += '<option value="' + category + '">' + category + '</option>';

    });
    $('#kt_datatable_search_category').html(options).selectpicker().on('change', function () {
        datatable.search($(this).val(), 'category');
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
