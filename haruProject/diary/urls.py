from django.urls import path
from .views import DiaryManager, DiaryTextBoxManager, DiaryStickerManager, Diaries


urlpatterns = [
    path('', Diaries.as_view(), name='diaries'),
    path('link/<int:diary_id>', DiaryManager.as_view(), name='diary_manager'),
    path('<int:diary_id>', Diaries.as_view()),
    path('textboxes', DiaryTextBoxManager.as_view(), name='diary_textbox_manager'),
    path('stickers', DiaryStickerManager.as_view(), name='diary_sticker_manager')
]