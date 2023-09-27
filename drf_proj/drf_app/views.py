from django.shortcuts import render
from logging import raiseExceptions
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import Http404
from .serializers import (
    LoginSerializer,
    CustomUserSerializer,
    SetNewPasswordSerializer,
    ResetPasswordEmailRequestSerializer,
    OtpSendSerializer, 
    VerifyOtpSerializer,
)
from .models import CustomUser
from .utils import Validators
import json
import os
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect
from django.http import Http404
User = get_user_model()
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

import logging
logger = logging.getLogger("error_log")

# Create your views here.
# login view
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = RefreshToken.for_user(user)
        
            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "data": {
                        'username':user.username,
                        'tokens':{
                            'access':str(tokens.access_token),
                            'refresh':str(tokens)
                        }
                    },
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )
        raise ValidationError(serializer.errors)

class RegistrationView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomUserSerializer
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()       
                return Response(
                    {
                        "success": True,
                        "status": status.HTTP_200_OK,
                        "data": serializer.data,
                        "message": "Login successful",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(str(e))
            return Response(
                {
                    "success": "False",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Not Found",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

# reset password
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get("email", "")

        if User.objects.filter(email=email.lower()).exists():
            user = User.objects.get(email=email.lower())
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            redirect_url = request.data.get("redirect_url", "")
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )

            absurl = "https://" + current_site + relativeLink
            email_body = (
                "Hello, \n Use link below to reset your password  \n"
                + absurl
                + "?redirect_url="
                + redirect_url
            )
            data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Reset your passsword",
            }
            Util.send_email(data)
            return Response(
                {"success": "We have sent you a link to reset your password"},
                status=status.HTTP_200_OK,
            )
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "False",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "User does not exists",
            }
            return Response(response, status=status_code)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        redirect_url = request.GET.get("redirect_url")

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):

                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + "?token_valid=False")
                else:
                    return CustomRedirect(
                        os.environ.get("FRONTEND_URL", "") + "?token_valid=False"
                    )

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url
                    + "?token_valid=True&message=Credentials Valid&uidb64="
                    + uidb64
                    + "&token="
                    + token
                )
            else:
                return CustomRedirect(os.environ.get("FRONTEND_URL", "") + "?token_valid=False")

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):

                    return CustomRedirect(redirect_url + "?token_valid=False")

            except UnboundLocalError as e:
                return Response(
                    {"error": "Token is not valid, please request a new one"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset success"}, status=status.HTTP_200_OK
        )
        
# for sending otp
class ServiceOtpSendView(generics.GenericAPIView):
    serializer_class = OtpSendSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="mobile",
                description="Provide mobile",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            
        ]
    )
    def post(self, request, *args, **kwargs):
        print("ki")
        print("requesttttttttt",request.data)
        mobile = request.GET.get("mobile")
        print(mobile)
        serializer = self.serializer_class(
            data=request.data, context={"mobile": mobile}
        )
        serializer.is_valid(raise_exception=True)
        try:
            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Otp Send",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": "False",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Not Found",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# for verify otp
class OtpVerifyView(generics.GenericAPIView):
    serializer_class = VerifyOtpSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="mobile",
                description="Provide mobile",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                name="order_id",
                description="Provide order id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        mobile = request.GET.get("mobile")
        print(mobile, "aa")
        order_id = request.GET.get("order_id")
        serializer = self.get_serializer(
            data=request.data, context={"mobile": mobile, "order_id": order_id}
        )
        if serializer.is_valid():
            data = {
                "success": True,
                "status": status.HTTP_200_OK,
                "message": "Otp Verified",
            }
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# addn for celery
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .tasks import add

@api_view(['POST'])
def addition_view(request):
    # arg1 = request.data.get('x')
    # arg2 = request.data.get('y')
    
    # Enqueue the task
    add.apply_async(args=[12, 89])
    
    return Response({"message": "Task started."}, status=status.HTTP_202_ACCEPTED)
