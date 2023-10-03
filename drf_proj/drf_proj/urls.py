"""
URL configuration for drf_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions
from django.conf.urls.static import static
from . import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

"""
	swagger settings are include here
"""


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/', include('drf_app.urls')),
    path('api/core/', include('core_app.urls')),
    path('api/test/', include('test_app.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
