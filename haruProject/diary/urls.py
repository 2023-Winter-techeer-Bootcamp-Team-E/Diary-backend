from django.urls import path # , re_path

from .views import DiaryManager, DiaryStickerManager, DiariesGet,DiariesPost, DiariesSave

#
# websocket_urlpatterns = [
#     re_path(r'ws/harurooms/(?P<diary_id>\w+)/$', consumers.HaruConsumer.as_asgi()),
#     ]

urlpatterns = [
    path('<int:diary_id>', DiariesGet.as_view(), name='diaries'),
    path('', DiariesPost.as_view(), name='diaries'),
    #path('save', Diaries.as_view(), name='diary_textbox_manager'),
    path('save', DiariesSave.as_view()),
    path('link', DiaryManager.as_view(), name='diary_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager'),
]
