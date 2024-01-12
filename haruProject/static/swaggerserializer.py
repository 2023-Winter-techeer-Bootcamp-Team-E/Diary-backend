from rest_framework import serializers

class StaticImageRequestSerializer(serializers.Serializer):
    size = serializers.IntegerField()
    page = serializers.IntegerField()


class StaticImageGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    data = StaticImageRequestSerializer()