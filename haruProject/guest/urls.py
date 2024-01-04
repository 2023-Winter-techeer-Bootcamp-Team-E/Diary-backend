from django.urls import path
from .views import CreateGuestView,CheckGuestPasswordView

urlpatterns = [
    # 기존의 path
    path('', CreateGuestView.as_view(), name='create_guest'),

    # 추가된 path
    # path('api/v1/guest/<int:guests_id>/', CreateGuestView.as_view(), name='specific_guest'),
    path('<int:guests_id>/', CheckGuestPasswordView.as_view(), name='check_guest_password'),

]
