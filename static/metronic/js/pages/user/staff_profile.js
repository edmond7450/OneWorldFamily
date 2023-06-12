"use strict";

var permission_datatable;
var KTDatatableDataLocal = function () {
    // initializer
    var init = function () {
        permission_datatable = $('#kt_permission_datatable').KTDatatable({
            // datasource definition
            data: {
                type: 'local',
                source: permissions,
                pageSize: 10,
            },

            // layout definition
            layout: {
                scroll: false, // enable/disable datatable scroll both horizontal and vertical when needed.
                // height: 450, // datatable's body's fixed height
                footer: false, // display/hide footer
            },

            // column sorting
            sortable: true,

            pagination: false,

            // columns definition
            columns: [
                {
                    field: 'index',
                    title: 'index',
                    width: 0,
                    visible: false,
                }, {
                    field: 'label',
                    title: 'Label',
                    overflow: 'visible',
                    template: function (row) {
                        return '<div class="font-weight-bolder font-size-lg mb-0 text-nowrap">' + row.label + '</div>';
                    }
                }, {
                    field: 'read',
                    title: 'Read',
                    width: 60,
                    template: function (row) {
                        if (row.read)
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="read" checked="checked"/>&nbsp;<span></span></label></div>';
                        else
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="read"/>&nbsp;<span></span></label></div>';
                    }
                }, {
                    field: 'update',
                    title: 'Update',
                    width: 60,
                    template: function (row) {
                        if (row.update)
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="update" checked="checked"/>&nbsp;<span></span></label></div>';
                        else
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="update"/>&nbsp;<span></span></label></div>';
                    }
                }, {
                    field: 'create',
                    title: 'Create',
                    width: 60,
                    template: function (row) {
                        if (row.create)
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="create" checked="checked"/>&nbsp;<span></span></label></div>';
                        else
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="create"/>&nbsp;<span></span></label></div>';
                    }
                }, {
                    field: 'delete',
                    title: 'Delete',
                    width: 60,
                    template: function (row) {
                        if (row.delete)
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="delete" checked="checked"/>&nbsp;<span></span></label></div>';
                        else
                            return '<div class="text-center"><label class="checkbox"><input type="checkbox" data-index="' + row.index + '" data-name="delete"/>&nbsp;<span></span></label></div>';
                    }
                }],
        });
    };

    return {
        // Public functions
        init: function () {
            init();

            $('#permission_modal .btn-primary').click(function () {
                var data = {};
                $('#permission_modal input[type="checkbox"]').each(function () {
                    if (data[$(this).data('index')] === undefined)
                        data[$(this).data('index')] = {};
                    data[$(this).data('index')][$(this).data('name')] = this.checked ? 1 : 0;
                });

                $.ajax({
                    type: 'PUT',
                    url: '/user/permission/',
                    data: {
                        user_id: $('#user_id').val(),
                        permissions: JSON.stringify(data)
                    },
                    dataType: 'json',
                    headers: {
                        'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
                    },
                    success: function (result) {
                        if (result.status === 200) {
                            toastr.success(result.message, 'Success');
                            $('#permission_modal').modal('hide');
                        } else {
                            toastr.error(result.message, 'Error');
                        }
                    }
                });

            });
        },
    };
}();

jQuery(document).ready(function () {
    if (is_super)
        KTDatatableDataLocal.init();
});