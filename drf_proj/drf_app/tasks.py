# Resource https://medium.com/swlh/asynchronous-task-with-django-celery-redis-and-production-using-supervisor-ef920725da03
from celery import shared_task
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from pathlib import Path
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


# for db backup
@shared_task
def backup():
    filename = "db"  # output filename here
    saveDir = open(settings.BASE_DIR / "{}.json".format(filename), "w")
    # change application_name with your django app which you want to get backup from it
    call_command(
        "dumpdata",
        [
            "drf_app",
            "core_app",
        ],
        stdout=saveDir,
        indent=4,
    )
    saveDir.close()

  
@shared_task
def add(x, y):
    return x + y
    