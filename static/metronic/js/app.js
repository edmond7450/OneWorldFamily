$(document).ready(function () {
    var link = $('#kt_aside_menu a[href="' + window.location.pathname + '"]');
    if (link.length === 0) {
        if (window.location.pathname === '/user/client/edit/')
            link = $('#kt_aside_menu a[href="/user/client/list/"]');
        else if (window.location.pathname === '/user/staff/edit/')
            link = $('#kt_aside_menu a[href="/user/staff/list/"]');
    }

    $('.menu-item').removeClass('menu-item-active');
    $(link).parent('.menu-item').addClass('menu-item-active');
    $(link).closest('.menu-item-submenu').addClass('menu-item-open menu-item-here');

    $('#kt_aside_menu li > a').click(function () {
        if ($(this).hasClass('menu-toggle')) return;

        // $('.menu-item').removeClass('menu-item-active');
        // $(this).parent('.menu-item').addClass('menu-item-active');
        $(this).children('span.menu-text').addClass('spinner spinner-sm spinner-right');

        setTimeout(function () {
            $('#kt_aside_menu li a span.menu-text').removeClass('spinner spinner-sm spinner-right');
        }, 5000);
    });
});