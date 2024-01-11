from rest_framework import serializers
from .models import StaticImage

class StaticImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticImage
        fields = ('st_image_url',)
