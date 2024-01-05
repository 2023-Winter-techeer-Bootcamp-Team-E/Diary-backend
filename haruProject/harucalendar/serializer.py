from .models import Harucalendar, Harucalendarsticker
from rest_framework import serializers


class HarucalendarAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harucalendar
        fields = '__all__'


class HarucalendarstickerAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harucalendarsticker
        fields = '__all__'
