from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntdeploy.settings')

app = Celery('ntdeploy')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://127.0.0.1:6379/1'
app.conf.result_backend = 'redis://127.0.0.1:6379/1'
# app.conf.broker_url = 'redis://192.168.30.48:6379/1'
# app.conf.result_backend = 'redis://192.168.30.48:6379/1'

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.imports = ('cmdb.logic',
                    'cmdb.util.ksyun_api',
                    'operating.jobs',
                    'operating.logic',
                    'server.logic',
                    'service.logic',
                    'grid.logic',
                    'api.ding.access_token')

app.conf.beat_schedule = {
    # 'run-ansible-sync-every-morning': {
    #     'task': 'cmdb.logic.cron_update',
    #     'schedule': crontab(hour=2, minute=30),
    # },
    # 'aliyun-ksyun-sync': {
    #     'task': 'cmdb.logic.cron_update_ali_ksyun_api',
    #     'schedule': crontab(minute='*/10'),
    # },
    # 'fetch_dingding_accesstoken': {
    #     'task': 'api.ding.access_token.main',
    #     'schedule': crontab(minute=30),
    # },
}

