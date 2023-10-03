from django.urls import path
from django.contrib import admin
from .views import print_numbers, DownloadView

urlpatterns = [
    path("print_numbers /", print_numbers, name="print_numbers"),
    path('download/', DownloadView.as_view(), name='download'),
]
