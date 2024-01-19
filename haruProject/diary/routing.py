from django.urls import re_path

from diary import consumers

websocket_urlpatterns = [
    re_path(r'ws/harurooms/(?P<diary_id>\w+)/$', consumers.HaruConsumer.as_asgi()),
]
