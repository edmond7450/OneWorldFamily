from django.urls import path

from back_app.views import dashboard
from back_app.views.manage import invoice, history, notification, question
from back_app.views.settings import profile, meta


urlpatterns = [
    path('', dashboard.DashboardView.as_view(), name='dashboard'),

    path('settings/profile/', profile.ProfileView.as_view(), name='settings_profile'),
    path('settings/profile/change_two_factor/', profile.change_two_factor, name='settings_profile_change_two_factor'),

    path('settings/meta/', meta.MetaView.as_view(), name='settings_meta'),

    path('manage/invoice/', invoice.InvoiceView.as_view(), name='manage_invoice'),

    path('manage/history/', history.HistoryView.as_view(), name='manage_history'),
    path('manage/notification/', notification.NotificationView.as_view(), name='manage_notification'),
    path('manage/question/', question.QuestionView.as_view(), name='manage_question'),
]
