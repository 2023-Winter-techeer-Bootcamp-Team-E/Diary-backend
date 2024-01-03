from django.urls import path
from .views import HarucalendarView,HarucalendarstickerView

urlpatterns = [

    path('<int:member_id>/', HarucalendarView.as_view()), #달력조회
    path('stickers', HarucalendarstickerView.as_view() ),
]