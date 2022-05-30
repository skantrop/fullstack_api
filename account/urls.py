from django.urls import path

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="registration"),
    path('login/', LoginView.as_view(), name="signin"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('check-token/', Check),
]