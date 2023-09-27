from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
)
from rest_framework_simplejwt.settings import api_settings

# from rest_framework_simplejwt import authentication
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import AnonymousUser

# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import BaseAuthentication


class CustomJwtAuth(JWTAuthentication):

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.exclude(status__in=["Deleted", "Inactive"]).get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")
            
        return user

from rest_framework.authentication import TokenAuthentication
import os


class ConditionalTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        custom_header = request.META.get("HTTP_AUTHORIZA")  # Replace with your custom header name
        print(custom_header)
        if custom_header:
            custom_header_token = custom_header.split(" ")[1]
            # if custom_header_token != os.getenv("WEB_TOKEN"):
            #     print("cccc", request.META.get("HTTP_AUTHORIZATION"))
            #     return super().authenticate(request)
            # return None
            if custom_header_token == os.getenv("WEB_TOKEN"):
                return None  # Return None to indicate successful conditional authentication
        else:
            auth = JWTAuthentication()
            return auth.authenticate(request)