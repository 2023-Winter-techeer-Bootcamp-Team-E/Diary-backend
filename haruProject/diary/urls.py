from django.urls import path
from .views import Diaries, DiaryManager

urlpatterns = [
    path('<int:diary_id>', Diaries.as_view()),
    path('', DiaryManager.as_view()),
    path('link/<int:diary_id>', DiaryManager.as_view()),
]