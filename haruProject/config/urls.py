from django.contrib import admin
from django.urls import path, include

from diary.views import Diaries

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('api/v1/members/', include('member.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/diaries', Diaries.as_view()),
    path('api/v1/diaries/', include('diary.urls')),
    path('api/v1/guests', include('guest.urls'))
]
