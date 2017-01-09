from __future__ import absolute_import

import os
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import Celery
from os import environ
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stump.settings')
from django.conf import settings 

broker_read_url = environ.get('RABBITMQ_BIGWIG_RX_URL', '')
broker_write_url = environ.get('RABBITMQ_BIGWIG_TX_URL', '')
app = Celery('stump')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.conf.update(
	 broker_read_url=broker_read_url,
     broker_write_url=broker_write_url,
     timezone='Europe/Moscow',
     enable_utc=True
)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

