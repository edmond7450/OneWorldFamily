from django.urls import path

from user_app.views.back import login, forgot, reset
from user_app.views.back import profile, coupon, staff_profile, staff_list, client_list

urlpatterns = [
    path('login/', login.LoginView.as_view(), name='user_login'),
    path('send_otp/', login.send_otp, name='user_send_otp'),
    path('check_otp/', login.check_otp, name='user_check_otp'),
    path('logout/', login.logout, name='user_logout'),

    path('forgot/', forgot.ForgotView.as_view(), name='user_forgot'),
    path('reset/<str:uidb64>/<str:token>', reset.ResetView.as_view(), name='reset'),

    path('profile/', profile.ProfileView.as_view(), name='user_profile'),
    path('coupon/', coupon.CouponListView.as_view(), name='user_coupon'),

    path('staff/list/', staff_list.StaffListView.as_view(), name='staff_list'),
    path('permission/', staff_profile.PermissionView.as_view(), name='user_permission'),

    path('client/list/', client_list.ClientListView.as_view(), name='client_list'),
]
