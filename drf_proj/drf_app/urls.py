from django.urls import path
from django.contrib import admin
from django.urls import path, include
from .views import (
    LoginAPIView,
    RegistrationView,
    SetNewPasswordAPIView,
    RequestPasswordResetEmail,
    PasswordTokenCheckAPI,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from .viewsets import (
    UserCredentialViewset,
    CustomerGetView,
)
from .views import ServiceOtpSendView, OtpVerifyView,addition_view

router = DefaultRouter()
router.register("usercredential", UserCredentialViewset, "usercredential")
router.register("getcustomers", CustomerGetView, "getcustomers")

urlpatterns = [
    path("", include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("login/", LoginAPIView.as_view()),
    path('register/', RegistrationView.as_view()),

    # reset password
    path("password-reset/", SetNewPasswordAPIView.as_view()),
    path("request-reset-email/", RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete/", SetNewPasswordAPIView.as_view(), name="password-reset-complete"
    ),

    # otp
    path("otp-send/", ServiceOtpSendView.as_view()),
    path("otp-verify/", OtpVerifyView.as_view()),
    # celery
    path("addition/", addition_view,name="addition"),

]
