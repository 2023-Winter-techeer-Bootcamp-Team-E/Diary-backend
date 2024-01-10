from rest_framework import serializers


class HarucalendarstickerRequestSerializer(serializers.Serializer):
    calendar_id = serializers.IntegerField()  # year
    sticker_image_url = serializers.CharField(max_length=20)  # month
    xcoor = serializers.IntegerField()
    ycoor = serializers.IntegerField()
    height = serializers.IntegerField()
    rolate = serializers.IntegerField()
    width = serializers.IntegerField()


class HarucalendarstickerGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()


class HarucalendarDiaryGetRequestSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()
    is_expired = serializers.BooleanField()
    diary_day = serializers.CharField()


class HarucalendarRequestSerializer(serializers.Serializer):
    calendar_id = serializers.IntegerField()
    year_month_day = serializers.CharField()


class HarucalendarGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    data = HarucalendarRequestSerializer()
    diaries = HarucalendarDiaryGetRequestSerializer(many=True)
