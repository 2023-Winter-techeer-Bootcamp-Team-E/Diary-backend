from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('api/v1/members/', include('member.urls'))
    path('admin/', admin.site.urls),
    path('api/v1/guests', include('guest.urls'))
]
