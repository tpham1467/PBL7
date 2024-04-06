import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBL7.settings')


app = Celery("PBL7", broker='redis://redis:6379/0',
             backend='redis://redis:6379')
app.conf.broker_url = 'redis://redis:6379/0'
app.conf.update(
    result_expires=3600,
)
app.config_from_object("django.conf.settings")

app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()