import requests
from django.conf import settings
from django.core.mail import EmailMessage
import threading
import os
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken 
from django.core.exceptions import ValidationError
user_model = get_user_model()
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class Validators:
    @staticmethod
    def validate_user_email(email_address:str)->bool:
        try:
            return True if not validate_email(email_address) else False
        except ValidationError:
            return False