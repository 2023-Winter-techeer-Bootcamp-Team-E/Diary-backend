from django.urls import path, re_path
from .views import HarucalendarView, HarucalendarstickerView

urlpatterns = [
    path('<int:member_id>', HarucalendarView.as_view()),

  #  re_path(r"^/(?P<year>\d{4})/(?P<month>\d{1,2})/$", HarucalendarView.as_view()),


    path('stickers', HarucalendarstickerView.as_view()),
]
