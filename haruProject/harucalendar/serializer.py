from .models import Harucalendar, Harucalendarsticker
from rest_framework import serializers


class HarucalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harucalendar
        fields = '__all__'

class HarucalendarstickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harucalendarsticker
        fields='__all__'
