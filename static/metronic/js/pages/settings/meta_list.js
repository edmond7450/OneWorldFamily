var datatable;

var KTDatatableRemoteAjax = function () {
    // initializer
    var init = function () {
        var width = $('.card-body').width() - 500;
        if (width < 100)
            width = 100;
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
                field: 'meta_key',
                title: 'Key',
                width: 100,
                autoHide: false,
            }, {
                field: 'meta_value',
                title: 'Value',
                width: width,
                template: function (row) {
                    return '<div class="text-nowrap" >' + row.meta_value + '</div>';
                },
            }, {
                field: 'updated_at',
                title: 'Update Date',
                type: 'date',
                format: 'MM/DD/YYYY',
                width: 100,
                template: function (row) {
                    return '<div class="text-muted">' + row.updated_at + '</div>';
                },
            }, {
                field: 'actions',
                title: 'Actions',
                sortable: false,
                width: 100,
                overflow: 'visible',
                autoHide: false,
                template: function (row) {
                    var output = '';
                    output += '<button class="btn-actions mr-2" onclick="edit_row(' + row.id + ')" title="Edit details">' +
                        '<span><svg height="14px" viewBox="0 0 512 511" width="14px" xmlns="http://www.w3.org/2000/svg"><path d="m405.332031 256.484375c-11.796875 0-21.332031 9.558594-21.332031 21.332031v170.667969c0 11.753906-9.558594 21.332031-21.332031 21.332031h-298.667969c-11.777344 0-21.332031-9.578125-21.332031-21.332031v-298.667969c0-11.753906 9.554687-21.332031 21.332031-21.332031h170.667969c11.796875 0 21.332031-9.558594 21.332031-21.332031 0-11.777344-9.535156-21.335938-21.332031-21.335938h-170.667969c-35.285156 0-64 28.714844-64 64v298.667969c0 35.285156 28.714844 64 64 64h298.667969c35.285156 0 64-28.714844 64-64v-170.667969c0-11.796875-9.539063-21.332031-21.335938-21.332031zm0 0"/><path d="m200.019531 237.050781c-1.492187 1.492188-2.496093 3.390625-2.921875 5.4375l-15.082031 75.4375c-.703125 3.496094.40625 7.101563 2.921875 9.640625 2.027344 2.027344 4.757812 3.113282 7.554688 3.113282.679687 0 1.386718-.0625 2.089843-.210938l75.414063-15.082031c2.089844-.429688 3.988281-1.429688 5.460937-2.925781l168.789063-168.789063-75.414063-75.410156zm0 0"/><path d="m496.382812 16.101562c-20.796874-20.800781-54.632812-20.800781-75.414062 0l-29.523438 29.523438 75.414063 75.414062 29.523437-29.527343c10.070313-10.046875 15.617188-23.445313 15.617188-37.695313s-5.546875-27.648437-15.617188-37.714844zm0 0"/></svg></span>' +
                        '</button>';
                    if (is_delete)
                        output += '<button class="btn-actions" onclick="delete_row(' + row.id + ')" title="Delete">' +
                            '<span><svg height="14px" viewBox="-40 0 427 427.00131" width="14px" xmlns="http://www.w3.org/2000/svg"><path d="m232.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/><path d="m114.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/><path d="m28.398438 127.121094v246.378906c0 14.5625 5.339843 28.238281 14.667968 38.050781 9.285156 9.839844 22.207032 15.425781 35.730469 15.449219h189.203125c13.527344-.023438 26.449219-5.609375 35.730469-15.449219 9.328125-9.8125 14.667969-23.488281 14.667969-38.050781v-246.378906c18.542968-4.921875 30.558593-22.835938 28.078124-41.863282-2.484374-19.023437-18.691406-33.253906-37.878906-33.257812h-51.199218v-12.5c.058593-10.511719-4.097657-20.605469-11.539063-28.03125-7.441406-7.421875-17.550781-11.5546875-28.0625-11.46875h-88.796875c-10.511719-.0859375-20.621094 4.046875-28.0625 11.46875-7.441406 7.425781-11.597656 17.519531-11.539062 28.03125v12.5h-51.199219c-19.1875.003906-35.394531 14.234375-37.878907 33.257812-2.480468 19.027344 9.535157 36.941407 28.078126 41.863282zm239.601562 279.878906h-189.203125c-17.097656 0-30.398437-14.6875-30.398437-33.5v-245.5h250v245.5c0 18.8125-13.300782 33.5-30.398438 33.5zm-158.601562-367.5c-.066407-5.207031 1.980468-10.21875 5.675781-13.894531 3.691406-3.675781 8.714843-5.695313 13.925781-5.605469h88.796875c5.210937-.089844 10.234375 1.929688 13.925781 5.605469 3.695313 3.671875 5.742188 8.6875 5.675782 13.894531v12.5h-128zm-71.199219 32.5h270.398437c9.941406 0 18 8.058594 18 18s-8.058594 18-18 18h-270.398437c-9.941407 0-18-8.058594-18-18s8.058593-18 18-18zm0 0"/><path d="m173.398438 154.703125c-5.523438 0-10 4.476563-10 10v189c0 5.519531 4.476562 10 10 10 5.523437 0 10-4.480469 10-10v-189c0-5.523437-4.476563-10-10-10zm0 0"/></svg></span>' +
                            '</button>';
                    return output
                }
            }];

        datatable = $('#kt_datatable').KTDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        url: '/back/settings/meta/',
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

    $(window).resize(function () {
        var width = $('.card-body').width() - 500;
        if (width < 100)
            width = 100;
        $('td[data-field="meta_value"] span').css('width', width);

        datatable.options.columns[3].width = width;
    });
});

$('#meta_data_modal .btn-primary').click(function () {
    $.ajax({
        url: '/back/settings/meta/',
        type: 'PUT',
        data: {
            'id': $('#meta_id').val(),
            'meta_key': $('#meta_key').val(),
            'meta_value': $('#meta_value').val()
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (result) {
            if (result.status === 200) {
                datatable.reload();
                toastr.success(result.message, 'Success');
                $('#meta_data_modal').modal('hide');
            } else {
                toastr.error(result.message, 'Error');
            }
        }
    });
});

function new_row() {
    $('#meta_id').val('');
    $('#meta_key').val('');
    $('#meta_value').val('');

    $('#meta_data_modal .btn-primary').removeClass('d-none').text('Add');

    $('#meta_data_modal').modal('show');
}

function edit_row(id) {
    $.ajax({
        url: '/back/settings/meta/',
        type: 'GET',
        data: {
            'id': id
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (result) {
            if (result.status === 200) {
                $('#meta_id').val(result.data.id);
                $('#meta_key').val(result.data.meta_key);
                $('#meta_value').val(result.data.meta_value);

                if (is_update)
                    $('#meta_data_modal .btn-primary').removeClass('d-none').text('Save');
                else
                    $('#meta_data_modal .btn-primary').addClass('d-none');

                $('#meta_data_modal').modal('show');

            } else {
                toastr.error(result.message, 'Error');
            }
        }
    });
}

function delete_row(id) {
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
                url: '/back/settings/meta/',
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
                        var data_index = datatable.originalDataSet.findIndex(x => x.id === id);
                        datatable.originalDataSet.splice(data_index, 1);
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
