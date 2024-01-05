from django.urls import path
from .views import Diaries, DiaryManager

urlpatterns = [
    path('', Diaries.as_view(), name='diaries'),
    path('link/<int:diary_id>', DiaryManager.as_view(), name='diary_manager'),
    path('<int:diary_id>', Diaries.as_view()),
]