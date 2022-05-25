from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema

from account.serializers import RegistrationSerializer, LoginSerializer, ChangePasswordSerializer, \
    ForgotPasswordSerializer, User, ForgotPasswordCompleteSerializer


class RegistrationView(APIView):
    @swagger_auto_schema(request_body=RegistrationSerializer())
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            message = """
            Вы успешно зарегистрировались! 
            Вам отправлено письмо с кодом активации.
            """
            return Response(message)

class ActivationView(APIView):
    def get(self, request, activation_code):
        User = get_user_model()
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Your account successfully activated!',
                        status=status.HTTP_200_OK)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer())
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_email()
            return Response('Вам на почту выслано сообщение')

class ForgotPasswordCompleteView(APIView):
    def get(self, request, email, code):
        request.data['verif_code'] = code
        request.data['email'] = email
        serializer = ForgotPasswordCompleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create_new_password()
            return Response('Вам на почту выслан новый пароль')
