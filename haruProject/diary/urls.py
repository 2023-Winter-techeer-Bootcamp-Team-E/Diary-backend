from django.urls import path
from .views import DiaryManager, DiaryStickerManager, Diaries, DiariesSave

urlpatterns = [
    path('', Diaries.as_view(), name='diaries'),
    #path('save', Diaries.as_view(), name='diary_textbox_manager'),
    path('save',DiariesSave.as_view()),
    path('link', DiaryManager.as_view(), name='diary_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager')
]
