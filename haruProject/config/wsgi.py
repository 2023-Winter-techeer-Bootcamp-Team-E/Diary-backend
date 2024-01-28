"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import eventlet
os.environ['EVENTLET_MONKEY_PATCH'] = '1'
# eventlet을 사용하려면 초기화 과정에서 monkey_patch()를 호출합니다.
eventlet.monkey_patch()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
