from django.urls import path
from .views import GuestCreateView

urlpatterns = [
    # 기존의 path
    path('<int:diary_id>/', GuestCreateView.as_view(), name='create_guest')
]