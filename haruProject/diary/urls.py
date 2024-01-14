from django.urls import path
from .views import DiariesGet,DiariesPost, DiaryManager, DiariesPut, DiaryStickerManager

urlpatterns = [
    path('', DiariesPost.as_view(), name='diaries'),
    path('link/<int:diary_id>', DiaryManager.as_view(), name='diary_manager'),
    path('<int:diary_id>', DiariesGet.as_view()),
    path('save', DiariesPut.as_view(), name='diary_textbox_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager')
]