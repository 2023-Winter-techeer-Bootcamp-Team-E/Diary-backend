from django.urls import path
from .views import HarucalendarView, HarucalendarstickerView

urlpatterns = [
    path('<int:member_id>/', HarucalendarView.as_view()),
    path('<int:calendar_id>/stickers/', HarucalendarstickerView.as_view()),
]
