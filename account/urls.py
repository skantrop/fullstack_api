from django.urls import path

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="registration"),
    path('activate/<str:activation_code>/', ActivationView.as_view()),
    path('login/', LoginView.as_view(), name="signin"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('forgot_password/', ForgotPasswordView.as_view(), name="forgot-password"),
    path('forgot_password_complete/<str:email>/<str:code>/', ForgotPasswordCompleteView.as_view(), name="forgot-password-complete"),
    path('check-token/', Check),
]