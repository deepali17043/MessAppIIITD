from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aahar.settings')
app = Celery('Aahar')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.beat_schedule = {
    'print-every-thrusday': {
        'task': 'demo_app.tasks.test',
        'schedule': crontab(hour=13, minute=57),
    },
}
app.conf.timezone = 'IST'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
