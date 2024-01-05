from django.contrib import admin
from django.urls import path, include
from harucalendar.views import HarucalendarView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/calendars', HarucalendarView.as_view()),
    path('api/v1/calendars/', include('harucalendar.urls')),
    path('api/v1/diaries/', include('diary.urls')),

]
