from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from . import models
from . import serializers
from core_app.permissions import (
    SuperUserOnly,
    DealerOnly,
    SupportadvisorOnly,
    SupportmanagerOnly,
    AdminOnly,
    SalesmanagerOnly,
    SalespersonOnly,
    MarketingOnly,
)
from core_app.pagination import CustomPagination
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model
from django.db.models import Q
import traceback
import json
User = get_user_model()
import logging
logger = logging.getLogger("error_log")

# for add, edit, get and delete user credentials
class UserCredentialViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    permission_classes_per_method = {
        # except for list and retrieve where both users with "write" or "read-only"
        # permissions can access the endpoints.
        "list": [
            SuperUserOnly
            | SalespersonOnly
            | SupportadvisorOnly
            | SupportmanagerOnly
            | AdminOnly
            | MarketingOnly
            | SalesmanagerOnly
        ],
        "create": [SuperUserOnly | SupportadvisorOnly | SupportmanagerOnly | AdminOnly],
        "partial_update": [SuperUserOnly | SupportadvisorOnly | SupportmanagerOnly | AdminOnly],
        "update": [SuperUserOnly | SupportadvisorOnly | SupportmanagerOnly | AdminOnly],
    }
    queryset = User.objects.filter(is_active="False").order_by(
        "-id"
    )
    serializer_class = serializers.UserCredentialSerializer
    pagination_class = CustomPagination
    search_fields = ["first_name", "email"]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = {
        "groups__name": ["exact"],
    }

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "message": "User added successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(str(e))
            return Response(
                {
                    "success": "False",
                    "status code": status.HTTP_400_BAD_REQUEST,
                    "message": "Not Found",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
# Getallcustomer
class CustomerGetView(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.filter(Q(groups__name="Customer") & ~Q(is_active=False)).order_by(
        "-id"
    )
    pagination_class = CustomPagination
    serializer_class = serializers.CustomerSerializer
    search_fields = ["first_name", "email"]
    filter_backends = (filters.SearchFilter,)
    http_method_names = ["get"]
