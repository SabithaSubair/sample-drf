from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import (
    CustomUser,
)
from django.contrib.auth import get_user_model
import random
import json
import requests
from datetime import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Permission, Group
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.conf import settings
from django.contrib import auth
import os
from pathlib import Path
from PIL import Image
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

# For Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email.lower(), password=password)
        if user:
            return user
        else:
            raise serializers.ValidationError("Invalid Credentials")

        return data

# For Registration
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = "__all__"
        read_only_fields = ["date_joined", "is_superuser", "groups","user_permissions","is_staff","is_active"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        password = User.objects.make_random_password()
        userdetails = User.objects.create(
            is_staff=False,
            **validated_data
        )        
        print(userdetails)
        # Send a welcome email to the user
        subject = 'Welcome to DRF App'
        message = 'Thank you for registering on DRF App.'
        from_email = settings.DEFAULT_FROM_EMAIL
        # recipient_list = ['sabitha@metrictreelabs.com']
        recipient_list = [userdetails.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return userdetails

# reset password
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ["email"]

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)
            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed("The reset link is invalid", 401)
        return super().validate(attrs)

class GroupCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


# user credential management
class UserCredentialSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    groups = GroupCredentialSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "user_type",
            "password",            
            "groups",
        ]
        read_only_fields = ["date_joined", "is_superuser", "user_permissions","is_staff","is_active"]

    def create(self, validated_data):
        usertype = validated_data.pop("user_type")
        my_group = Group.objects.get(name=usertype)
        if usertype == "Customer":
            user = User.objects.create(is_staff=False, **validated_data)
        else:
            user = User.objects.create(is_staff=True, **validated_data)
        user.status = "Active"
        user.save()
        my_group.user_set.add(user)
        # Send a welcome email to the user
        subject = 'Welcome to DRF App'
        message = 'Successfully registered on DRF App.'
        from_email = settings.DEFAULT_FROM_EMAIL
        # recipient_list = ['sabitha@metrictreelabs.com']
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return user

# customer serializer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

# signup and login otp sending for userapp
class OtpSendSerializer(serializers.Serializer):
    otp = serializers.CharField(read_only=True)

    def validate(self, validated_data):
        print("vvvvvvvvvvv",validated_data)
        mobile = self.context.get("mobile")
        if not str(mobile).isdigit():
            raise serializers.ValidationError({"error": "Invalid Phone number!"})
        if len(mobile) != 10:
            raise serializers.ValidationError({"error": "Invalid Phone number!"})

        otp = 1234  # random.randint(1000, 9999)
        userdata = ServiceConsent.objects.create(otp=otp)
        # print(userdata)

        return {"phone": mobile, "otp": otp}

# signup and login otp verification for userapp
class VerifyOtpSerializer(serializers.Serializer):
    otp_to_verify = serializers.CharField(write_only=True)
    tokens = serializers.JSONField(read_only=True)
    email = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    def validate(self, validated_data):
        service_otp = validated_data.get("otp_to_verify", "")
        phonenumber = self.context.get("mobile")
        order_id = self.context.get("order_id")

        # if len(user_otp) != 4:
        #     raise serializers.ValidationError({"error": "Please Enter 4 digits"})
        try:
            service_consent = ServiceConsent.objects.filter(order_id=order_id).last()
        except Exception:
            raise serializers.ValidationError({"error": "otp not found!.."})
        if int(service_otp) != service_consent.otp:
            raise serializers.ValidationError({"error": "Invalid otp"})
        if (
            datetime.now() - service_consent.updated_at
        ).total_seconds() > settings.OTP_EXPIRY and int(service_otp) == service_consent.otp:
            raise serializers.ValidationError({"error": "otp expired!"})

        service_consent.verified = True
        service_consent.save()
        return {
            "phone": phonenumber,
        }
