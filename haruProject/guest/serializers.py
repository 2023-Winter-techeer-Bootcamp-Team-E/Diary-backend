from rest_framework import serializers
from .models import Guest


class GuestCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Guest
            fields = ['guest_pw', 'diary', 'guest_id']

        def create(self, validated_data):
            return Guest.objects.create(**validated_data)