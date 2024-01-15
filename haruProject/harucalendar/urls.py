from django.urls import path, re_path
from .views import HarucalendarView, HarucalendarstickerView

urlpatterns = [
    path('', HarucalendarView.as_view()),
    path('stickers', HarucalendarstickerView.as_view()),


]
