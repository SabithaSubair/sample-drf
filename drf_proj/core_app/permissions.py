from rest_framework import permissions
import os


class SuperUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "admin":
                return True


class DealerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "dealer":
                return True


class SalespersonOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "sales executive":
                return True


class MarketingOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "marketing":
                return True


class SupportmanagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "support manager":
                return True


class SupportadvisorOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "support advisor":
                return True


class CustomerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "customer":
                return True


class SalesmanagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list("name", flat=True)
        usergoup = list(group)
        if usergoup:
            if usergoup[0].lower() == "sales manager":
                return True


class PermissionPolicyMixin:
    def check_permissions(self, request):
        try:
            # This line is heavily inspired from `APIView.dispatch`.
            # It returns the method associated with an endpoint.
            handler = getattr(self, request.method.lower())
        except AttributeError:
            handler = None

        if (
            handler
            and self.permission_classes_per_method
            and self.permission_classes_per_method.get(handler.__name__)
        ):
            self.permission_classes = self.permission_classes_per_method.get(handler.__name__)

        super().check_permissions(request)


class WebAuthentication(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key_header = request.META.get("HTTP_X_APIKEY")
        api_key = os.getenv("WEB_TOKEN")
        has_valid_api_key = bool(api_key == api_key_header)
        is_authenticated = False
        try:
            if request.user.is_authenticated:
                is_authenticated = True
        except:
            pass
        public_perm = has_valid_api_key or is_authenticated
        return bool(public_perm)
