from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.decorators import api_view

from .models import User
from account.serializers import RegistrationSerializer, ProfileSerializer

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


@api_view(["GET"])
def Check(request):
    if request.user.is_authenticated: return HttpResponse("using token")
    return HttpResponseForbidden("token invalid or expired")

@api_view(["DELETE"])
def DeleteUserView(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseForbidden("token invalid or expired")
    if user.is_staff:
        return HttpResponseForbidden("User is superuser")
    user.delete()
    return Response("User successfully deleted", 204)

@api_view(["GET"])
def profile_api_view(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseForbidden("token invalid or expired")
    ser = ProfileSerializer(user)
    return Response(ser.data)
