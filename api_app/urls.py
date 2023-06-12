from django.urls import path
from dj_rest_auth.views import LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import meta
from .views.payment import invoice, order, method, stripe_card, stripe_webhook
from .views.security import login, device
from .views.user import signup, forgot, profile, setting, notification

urlpatterns = [
    # path('security/login/', TokenObtainPairView.as_view(), name='api_security_login'),
    path('security/login/', login.LoginView.as_view(), name='api_security_login'),
    path('security/otp/', login.OTPView.as_view(), name='api_security_otp'),
    path('security/refresh/', TokenRefreshView.as_view(), name='api_security_refresh'),
    path('security/logout/', LogoutView.as_view(), name='rest_logout'),
    path('security/device/', device.DeviceView.as_view(), name='api_security_device'),

    path('get/<str:meta_key>/', meta.MetaView.as_view(), name='api_meta_get'),

    # path('download/<str:filepath>/', tests.download, name='api_download'),

    path('user/check-email/', signup.CheckEmailView.as_view(), name='api_user_check_email'),
    path('user/create-new-user/', signup.RegisterView.as_view(), name='api_user_register'),
    path('user/resend-email-code/', signup.SendEmailView.as_view(), name='api_user_send_email_code'),
    path('user/verify-email/', signup.VerifyEmailView.as_view(), name='api_user_verify_email'),

    path('user/save-phone-number/', signup.SavePhoneView.as_view(), name='api_user_save_phone'),
    path('user/resend-phone-code/', signup.SendSMSView.as_view(), name='api_user_send_phone_code'),
    path('user/verify-phone/', signup.VerifyPhoneView.as_view(), name='api_user_verify_phone'),

    path('user/forgot/', forgot.ForgotView.as_view(), name='api_user_forgot'),
    path('user/reset/', forgot.ResetView.as_view(), name='api_user_reset'),
    path('user/check-password-token/', forgot.CheckView.as_view(), name='api_user_check_password_token'),
    path('user/set-new-password/', forgot.NewSetView.as_view(), name='api_user_set_new_password'),

    path('user/check-password/', profile.CheckPasswordView.as_view(), name='api_user_check_password'),
    path('user/profile/', profile.ProfileView.as_view(), name='api_user_profile'),
    path('user/setting/<str:meta_key>/', setting.SettingView.as_view(), name='api_user_setting'),
    path('user/notification/', notification.NotificationView.as_view(), name='api_user_notification'),

    path('payment/method/', method.PaymentMethodView.as_view(), name='api_payment_method'),
    path('card/', stripe_card.CardView.as_view(), name='api_stripe_card'),
    path('card/token/', stripe_card.CardTokenView.as_view(), name='api_stripe_card_token'),
    path('stripe/webhook/', stripe_webhook.endpoint, name='stripe_webhook_endpoint'),
    path('order/', order.OrderView.as_view(), name='api_stripe_order'),
    path('invoice/', invoice.InvoiceView.as_view(), name='api_invoice'),
]
