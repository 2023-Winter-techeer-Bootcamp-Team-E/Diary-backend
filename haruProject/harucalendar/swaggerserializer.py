from rest_framework import serializers


class HarucalendarstickerSerializer(serializers.Serializer):
    sticker_image_url = serializers.CharField()
    top = serializers.IntegerField()
    left = serializers.IntegerField()
    height = serializers.IntegerField()
    rotate = serializers.IntegerField()
    width = serializers.IntegerField()


class HarucalendarstickerRequestSerializer(serializers.Serializer):
    stickers = serializers.ListField(child=HarucalendarstickerSerializer())


class HarucalendarstickerGetResponseSerializer(serializers.Serializer):
    calendar_id = serializers.IntegerField()
    year_month = serializers.IntegerField()
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()


class HarucalendarDiaryGetRequestSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()
    day = serializers.CharField()
    created_at = serializers.DateTimeField()
    is_expired = serializers.BooleanField()


class HarucalendarRequestSerializer(serializers.Serializer):
    year_month = serializers.CharField()


class HarucalendarGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    data = HarucalendarRequestSerializer()
    diaries = HarucalendarDiaryGetRequestSerializer(many=True)
