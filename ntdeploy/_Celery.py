#!/usr/bin/env python
# coding:utf-8

import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntdeploy.settings')

app = Celery('ntdeploy')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


def main():
    pass

if __name__ == '__main__':
    main()

