from django.urls import path, re_path
from .views import StaticImageView

urlpatterns = [
    path('stickers', StaticImageView.as_view())
]
