"use strict";

// Class definition
var KTWidgets = function () {
    // Private properties
    // General Controls
    var _initDaterangepicker = function _initDaterangepicker() {
        if ($('#kt_dashboard_daterangepicker').length == 0) {
            return;
        }

        var picker = $('#kt_dashboard_daterangepicker');
        var start = moment();
        var end = moment();

        function cb(start, end, label) {
            var title = '';
            var range = '';

            if (end - start < 100 || label == 'Today') {
                title = 'Today:';
                range = start.format('MMM D');
            } else if (label == 'Yesterday') {
                title = 'Yesterday:';
                range = start.format('MMM D');
            } else {
                range = start.format('MMM D') + ' - ' + end.format('MMM D');
            }

            $('#kt_dashboard_daterangepicker_date').html(range);
            $('#kt_dashboard_daterangepicker_title').html(title);
        }

        picker.daterangepicker({
            direction: KTUtil.isRTL(),
            startDate: start,
            endDate: end,
            opens: 'left',
            applyClass: 'btn-primary',
            cancelClass: 'btn-light-primary',
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            }
        }, cb);
        cb(start, end, '');
    };

    // Charts widgets
    var _initMixedIncomeChart = function _initMixedIncomeChart() {
        var element = document.getElementById("kt_mixed_income_chart");
        var height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }

        var strokeColor = '#2F8C83';
        var options = {
            series: [{
                name: 'Income',
                data: chart_data['income']['series']
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 0,
                    blur: 3,
                    color: strokeColor,
                    opacity: 0.5
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 0
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [strokeColor]
            },
            xaxis: {
                categories: chart_data['income']['categories'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: chart_data['income']['min_y'],
                max: chart_data['income']['max_y'],
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        if (val >= 0)
                            return "$" + val.toFixed(2) + " USD";
                        else
                            return "($" + Math.abs(val).toFixed(2) + " USD)";
                    }
                },
                marker: {
                    show: false
                }
            },
            colors: ['transparent'],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light']['success']],
                strokeColor: [strokeColor],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initStatsUserChart = function _initStatsUserChart() {
        var element = document.getElementById("kt_stats_user_chart");
        var height = parseInt(KTUtil.css(element, 'height'));
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'primary';

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'New Users',
                data: chart_data['user']['series']
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: chart_data['user']['categories'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: 0,
                max: chart_data['user']['max_y'],
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return val;
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initStatsFeedChart = function _initStatsFeedChart() {
        var element = document.getElementById("kt_stats_feed_chart");
        var height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'New Feeds',
                data: chart_data['feed']['series']
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base']['primary']]
            },
            xaxis: {
                categories: chart_data['feed']['categories'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: 0,
                max: chart_data['feed']['max_y'],
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return val;
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light']['primary']],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light']['primary']],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base']['primary']],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initStatsLoginChart = function _initStatsLoginChart() {
        var element = document.getElementById("kt_stats_login_chart");
        var height = parseInt(KTUtil.css(element, 'height'));
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'primary';

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'New Logins',
                data: chart_data['login']['series']
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: chart_data['login']['categories'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: 0,
                max: chart_data['login']['max_y'],
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return val;
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };


    // Tiles
    var _initTilesWidget1 = function _initTilesWidget1() {
        var element = document.getElementById("kt_tiles_widget_1_chart");
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'primary';
        var height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [20, 22, 30, 28, 25, 26, 30, 28, 22, 24, 25, 35]
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'gradient',
                opacity: 1,
                gradient: {
                    type: "vertical",
                    shadeIntensity: 0.55,
                    gradientToColors: undefined,
                    inverseColors: true,
                    opacityFrom: 1,
                    opacityTo: 0.2,
                    stops: [25, 50, 100],
                    colorStops: []
                }
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: {
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 37,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return "$" + val + " thousands";
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            },
            padding: {
                top: 0,
                bottom: 0
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initTilesWidget2 = function _initTilesWidget2() {
        var element = document.getElementById("kt_tiles_widget_2_chart");
        var height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }

        var strokeColor = KTUtil.changeColor(KTApp.getSettings()['colors']['theme']['base']['danger']);
        var fillColor = KTUtil.changeColor(KTApp.getSettings()['colors']['theme']['base']['danger']);
        var options = {
            series: [{
                name: 'Net Profit',
                data: [10, 10, 20, 20, 12, 12]
            }],
            chart: {
                type: 'area',
                height: height,
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                },
                padding: {
                    top: 0,
                    bottom: 0
                }
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [strokeColor]
            },
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 22,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function formatter(val) {
                            return val + "";
                        }
                    }
                }
            },
            colors: [fillColor],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light']['danger']],
                strokeColor: [strokeColor],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initTilesWidget5 = function _initTilesWidget5() {
        var element = document.getElementById("kt_tiles_widget_5_chart");
        var height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [10, 15, 18, 14]
            }, {
                name: 'Revenue',
                data: [8, 13, 16, 12]
            }],
            chart: {
                type: 'bar',
                height: height,
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                },
                padding: {
                    left: 20,
                    right: 20
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: ['25%'],
                    endingShape: 'rounded'
                }
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: ['solid', 'gradient'],
                opacity: 0.25
            },
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May']
            },
            yaxis: {
                min: 0,
                max: 20
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function formatter(val) {
                            return val + "";
                        }
                    }
                },
                marker: {
                    show: false
                }
            },
            colors: ['#ffffff', '#ffffff']
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initTilesWidget8 = function _initTilesWidget8() {
        var element = document.getElementById("kt_tiles_widget_8_chart");
        var height = parseInt(KTUtil.css(element, 'height'));
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'danger';

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [20, 20, 30, 15, 40, 30]
            }],
            chart: {
                type: 'area',
                height: 150,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid'
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: {
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 45,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return "$" + val + " thousands";
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            },
            padding: {
                top: 0,
                bottom: 0
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initTilesWidget17 = function _initTilesWidget17() {
        var element = document.getElementById("kt_tiles_widget_17_chart");

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [10, 20, 20, 8]
            }],
            chart: {
                type: 'area',
                height: 150,
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                },
                padding: {
                    top: 0,
                    bottom: 0
                }
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base']['success']]
            },
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 22,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function formatter(val) {
                            return val + "";
                        }
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light']['success']],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light']['success']],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base']['success']],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initTilesWidget20 = function _initTilesWidget20() {
        var element = document.getElementById("kt_tiles_widget_20_chart");

        if (!element) {
            return;
        }

        var options = {
            series: [74],
            chart: {
                height: 250,
                type: 'radialBar',
                offsetY: 0
            },
            plotOptions: {
                radialBar: {
                    startAngle: -90,
                    endAngle: 90,
                    hollow: {
                        margin: 0,
                        size: "70%"
                    },
                    dataLabels: {
                        showOn: "always",
                        name: {
                            show: true,
                            fontSize: "13px",
                            fontWeight: "400",
                            offsetY: -5,
                            color: KTApp.getSettings()['colors']['gray']['gray-300']
                        },
                        value: {
                            color: KTApp.getSettings()['colors']['theme']['inverse']['primary'],
                            fontSize: "22px",
                            fontWeight: "bold",
                            offsetY: -40,
                            show: true
                        }
                    },
                    track: {
                        background: KTUtil.changeColor(KTApp.getSettings()['colors']['theme']['base']['primary'], -7),
                        strokeWidth: '100%'
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['inverse']['primary']],
            stroke: {
                lineCap: "round"
            },
            labels: ["Progress"]
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initMixedWidget21 = function _initMixedWidget21() {
        var element = document.getElementById("kt_tiles_widget_21_chart");
        var height = parseInt(KTUtil.css(element, 'height'));
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'info';

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [20, 20, 30, 15, 30, 30]
            }],
            chart: {
                type: 'area',
                height: height,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: {
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 32,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return "$" + val + " thousands";
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    };

    var _initMixedWidget23 = function _initMixedWidget23() {
        var element = document.getElementById("kt_tiles_widget_23_chart");
        var height = parseInt(KTUtil.css(element, 'height'));
        var color = KTUtil.hasAttr(element, 'data-color') ? KTUtil.attr(element, 'data-color') : 'primary';

        if (!element) {
            return;
        }

        var options = {
            series: [{
                name: 'Net Profit',
                data: [15, 25, 15, 40, 20, 50]
            }],
            chart: {
                type: 'area',
                height: 125,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {},
            legend: {
                show: false
            },
            dataLabels: {
                enabled: false
            },
            fill: {
                type: 'solid',
                opacity: 1
            },
            stroke: {
                curve: 'smooth',
                show: true,
                width: 3,
                colors: [KTApp.getSettings()['colors']['theme']['base'][color]]
            },
            xaxis: {
                categories: ['Jan, 2020', 'Feb, 2020', 'Mar, 2020', 'Apr, 2020', 'May, 2020', 'Jun, 2020'],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                },
                crosshairs: {
                    show: false,
                    position: 'front',
                    stroke: {
                        color: KTApp.getSettings()['colors']['gray']['gray-300'],
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: {
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            yaxis: {
                min: 0,
                max: 55,
                labels: {
                    show: false,
                    style: {
                        colors: KTApp.getSettings()['colors']['gray']['gray-500'],
                        fontSize: '12px',
                        fontFamily: KTApp.getSettings()['font-family']
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: 'none',
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'none',
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: '12px',
                    fontFamily: KTApp.getSettings()['font-family']
                },
                y: {
                    formatter: function formatter(val) {
                        return "$" + val + " thousands";
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
            markers: {
                colors: [KTApp.getSettings()['colors']['theme']['light'][color]],
                strokeColor: [KTApp.getSettings()['colors']['theme']['base'][color]],
                strokeWidth: 3
            }
        };
        var chart = new ApexCharts(element, options);
        chart.render();
    }; // Forms


    var _initFormsWidget1 = function _initFormsWidget1() {
        var inputEl = KTUtil.getById("kt_forms_widget_1_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget2 = function _initFormsWidget2() {
        var formEl = KTUtil.getById("kt_forms_widget_2_form");
        var editorId = 'kt_forms_widget_2_editor'; // init editor

        var options = {
            modules: {
                toolbar: {
                    container: "#kt_forms_widget_2_editor_toolbar"
                }
            },
            placeholder: 'Type message...',
            theme: 'snow'
        };

        if (!formEl) {
            return;
        } // Init editor


        var editorObj = new Quill('#' + editorId, options);
    };

    var _initFormsWidget3 = function _initFormsWidget3() {
        var inputEl = KTUtil.getById("kt_forms_widget_3_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget4 = function _initFormsWidget4() {
        var inputEl = KTUtil.getById("kt_forms_widget_4_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget5 = function _initFormsWidget5() {
        var inputEl = KTUtil.getById("kt_forms_widget_5_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget6 = function _initFormsWidget6() {
        var inputEl = KTUtil.getById("kt_forms_widget_6_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget7 = function _initFormsWidget7() {
        var inputEl = KTUtil.getById("kt_forms_widget_7_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget8 = function _initFormsWidget8() {
        var inputEl = KTUtil.getById("kt_forms_widget_8_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget9 = function _initFormsWidget9() {
        var inputEl = KTUtil.getById("kt_forms_widget_9_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget10 = function _initFormsWidget10() {
        var inputEl = KTUtil.getById("kt_forms_widget_10_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget11 = function _initFormsWidget11() {
        var inputEl = KTUtil.getById("kt_forms_widget_11_input");

        if (inputEl) {
            autosize(inputEl);
        }
    };

    var _initFormsWidget12 = function _initFormsWidget12() {
        var inputEl = KTUtil.getById("kt_forms_widget_12_input");

        if (inputEl) {
            autosize(inputEl);
        }
    }; // Advance Tables


    var _initAdvancedTableGroupSelection = function _initAdvancedTableGroupSelection(element) {
        var table = KTUtil.getById(element);

        if (!table) {
            return;
        }

        KTUtil.on(table, 'thead th .checkbox > input', 'change', function (e) {
            var checkboxes = KTUtil.findAll(table, 'tbody td .checkbox > input');

            for (var i = 0, len = checkboxes.length; i < len; i++) {
                checkboxes[i].checked = this.checked;
            }
        });
    };

    var _initPriceSlider = function _initPriceSlider(element) {
        // init slider
        var slider = document.getElementById(element);

        if (typeof slider === 'undefined') {
            return;
        }

        if (!slider) {
            return;
        }

        noUiSlider.create(slider, {
            start: [20, 60],
            connect: true,
            range: {
                'min': 0,
                'max': 100
            }
        });
    }; // Education Show More Demo


    var _initEducationShowMoreBtn = function _initEducationShowMoreBtn() {
        var el = KTUtil.getById('kt_app_education_more_feeds_btn');

        if (!el) {
            return;
        }

        KTUtil.addEvent(el, 'click', function (e) {
            var elements = document.getElementsByClassName('education-more-feeds');

            if (!elements || elements.length <= 0) {
                return;
            }

            KTUtil.btnWait(el, 'spinner spinner-right spinner-white pr-15', 'Please wait...', true);
            setTimeout(function () {
                KTUtil.btnRelease(el);
                KTUtil.addClass(el, 'd-none');
                var item;

                for (var i = 0, len = elements.length; i < len; i++) {
                    item = elements[0];
                    KTUtil.removeClass(elements[i], 'd-none');
                    var textarea = KTUtil.find(item, 'textarea');

                    if (textarea) {
                        autosize(textarea);
                    }
                }

                KTUtil.scrollTo(item);
            }, 1000);
        });
    };


    // Public methods
    return {
        init: function init() {
            // General Controls
            _initDaterangepicker();

            // Chart Widgets
            _initMixedIncomeChart();
            _initStatsUserChart();
            _initStatsFeedChart();
            _initStatsLoginChart();

            // Tiles Widgets
            _initTilesWidget1();

            _initTilesWidget2();

            _initTilesWidget5();

            _initTilesWidget8();

            _initTilesWidget17();

            _initTilesWidget20();

            _initMixedWidget21();

            _initMixedWidget23(); // Table Widgets


            _initAdvancedTableGroupSelection('kt_advance_table_widget_1');

            _initAdvancedTableGroupSelection('kt_advance_table_widget_2');

            _initAdvancedTableGroupSelection('kt_advance_table_widget_3');

            _initAdvancedTableGroupSelection('kt_advance_table_widget_4'); // Form Widgets


            _initPriceSlider('kt_price_slider'); // Forms widgets


            _initFormsWidget1();

            _initFormsWidget2();

            _initFormsWidget3();

            _initFormsWidget4();

            _initFormsWidget5();

            _initFormsWidget6();

            _initFormsWidget7();

            _initFormsWidget8();

            _initFormsWidget9();

            _initFormsWidget10();

            _initFormsWidget11(); // Education App


            _initEducationShowMoreBtn();
        }
    };
}(); // Webpack support


jQuery(document).ready(function () {
    KTWidgets.init();
});
