from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django 설정을 불러옵니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery 앱을 생성합니다.
app = Celery('haruProject')

# Django 설정으로부터 Celery 설정을 가져옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 등록된 장고 앱 설정에서 task 불러오기
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
