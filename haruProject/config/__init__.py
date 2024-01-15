from __future__ import absolute_import, unicode_literals

# 이렇게 Celery 앱을 등록합니다.
from .celery import app as celery_app

__all__ = ('celery_app',)