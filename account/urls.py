from django.urls import path, include

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="registration"),
    # path('activate/', ActivationView.as_view(), name="activation"),
    path('activate/<str:activation_code>/', ActivationView.as_view()),
    path('login/', LoginView.as_view(), name="signin"),
    # path('logout/', LogoutView.as_view(), name="signout"),
    path('forgot_pass/', ForgotPasswordView.as_view(), name="forgot-password"),
    path('change_password/', ChangePasswordView.as_view(), name="change-password"),

    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]