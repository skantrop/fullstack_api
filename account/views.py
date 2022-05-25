from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView

from account.serializers import RegistrationSerializer, LoginSerializer, ChangePasswordSerializer, \
    ForgotPasswordSerializer, User


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            message = """
            Вы успешно зарегистрировались! 
            Вам отправлено письмо с кодом активации.
            """
            return Response(message)


# class ActivationView(APIView):
#     def post(self, request):
#         serializer = ActivationSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.activate()
#             return Response('Вы успешно активированы')


class ActivationView(APIView):
    def get(self, request, activation_code):
        User = get_user_model()
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Your account successfully activated!',
                        status=status.HTTP_200_OK)

# class LoginView(ObtainAuthToken):
#     serializer_class = LoginSerializer

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         Token.objects.filter(user=user).delete()
#         return Response('Вы успешно вышли')


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create_new_password()
            return Response('Вам на почту выслан новый пароль')


# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid(raise_exception=True):
#             serializer.set_new_password()
#             return Response('Пароль успешно обновлен')


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model() # your user model
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user