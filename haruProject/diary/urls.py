from django.urls import path
from .views import Diaries, DiaryManager,DiaryTextBoxManager

urlpatterns = [
    path('', Diaries.as_view(), name='diaries'),
    path('<int:diary_id>', Diaries.as_view()),
    path('link/<int:diary_id>', DiaryManager.as_view(), name='diary_manager'),
    path('textboxes', DiaryTextBoxManager.as_view(), name='diary_textbox_manager')
]