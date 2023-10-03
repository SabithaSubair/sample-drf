from django.urls import path
from django.contrib import admin
from .views import print_numbers

urlpatterns = [
    path("print_numbers /", print_numbers, name="print_numbers"),
]