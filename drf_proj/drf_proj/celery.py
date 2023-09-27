from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
import dotenv
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_proj.settings")
# env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), ".env")
# dotenv.load_dotenv(env_file)

app = Celery("drf_proj")
# print(settings.EMAIL_HOST)

app.config_from_object("django.conf:settings",namespace='CELERY')

app.conf.beat_schedule = {
    "every_12_hours": {
        "task": "drf_app.tasks.backup",
        "schedule": crontab(minute=0, hour="12,0"),
    }
}


app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
