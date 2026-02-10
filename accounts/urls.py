from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('verify-sent/', views.verify_sent_view, name='verify_sent'),
    path('verify/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),

    path('verify-pending/<uidb64>/',
         views.verify_pending_view, name='verify_pending'),
    path('verify-sms/<uidb64>/', views.verify_sms_view, name='verify_sms'),
    path('resend-sms/<uidb64>/', views.resend_sms_view, name='resend_sms'),
]
