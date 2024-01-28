from django.urls import path # , re_path

from . import views, consumers
from .views import DiaryManager, DiaryStickerManager, Diaries, DiariesSave, HaruRoomManager

#
# websocket_urlpatterns = [
#     re_path(r'ws/harurooms/(?P<diary_id>\w+)/$', consumers.HaruConsumer.as_asgi()),
#     ]

urlpatterns = [
    path('', Diaries.as_view(), name='diaries'),
    #path('save', Diaries.as_view(), name='diary_textbox_manager'),
    path('save', DiariesSave.as_view()),
    path('link', DiaryManager.as_view(), name='diary_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager'),
    path("harurooms/<int:diary_id>/", HaruRoomManager.as_view()),
    path("haruroom/<int:diaryid>/", views.room, name="room"),
]
