from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.decorators import api_view

from account.serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    @swagger_auto_schema(request_body=RegistrationSerializer())
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            message = """
            Вы успешно зарегистрировались! 
            """
            return Response(message)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

@api_view(["GET"])
def Check(request):
    if request.user.is_authenticated: return HttpResponse("using token")
    return HttpResponseForbidden("token invalid or expired")
