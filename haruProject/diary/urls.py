from django.urls import path
from .views import DiaryManager, DiaryStickerManager, Diaries

urlpatterns = [
    #path('', Diaries.as_view(), name='diaries'),
    #path('save', Diaries.as_view(), name='diary_textbox_manager'),
    path('<int:diary_id>', Diaries.as_view()),
    path('link/<int:diary_id>', DiaryManager.as_view(), name='diary_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager')
]
