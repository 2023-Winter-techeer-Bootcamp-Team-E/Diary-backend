from diary import serializers
from rest_framework import serializers


class DiaryTextBoxGetSerializer(serializers.Serializer):
    textbox_id = serializers.IntegerField()
    writer = serializers.CharField()
    content = serializers.CharField()
    xcoor = serializers.IntegerField()
    ycoor = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    rotate = serializers.IntegerField()


class DiaryStickerGetSerializer(serializers.Serializer):
    sticker_id = serializers.IntegerField()
    sticker_image_url = serializers.CharField()
    xcoor = serializers.IntegerField()
    ycoor = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    rotate = serializers.IntegerField()


class DiaryGetRequestSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()


class DiaryGetResponseSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()
    diary_date = serializers.CharField()
    diary_bg_url = serializers.CharField()
    is_expiry = serializers.BooleanField()
    diaryTextBoxs = DiaryTextBoxGetSerializer(many=True)
    diaryStickers = DiaryStickerGetSerializer(many=True)


class DiaryLinkResponseSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()
    diary_date = serializers.CharField()
    sns_link = serializers.URLField()


class DiaryLinkGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    data = DiaryLinkResponseSerializer()

'''
class DiaryTextBoxPostRequestSerializer(serializers.Serializer):
    content = serializers.CharField()
    diary_id = serializers.IntegerField()


class DiaryTextBoxPostResponseSerializer(serializers.Serializer):
    textbox_id = serializers.IntegerField()
'''

class TextBoxPutRequestSerializer(serializers.Serializer):
    writer = serializers.CharField()
    xcoor = serializers.IntegerField()
    ycoor = serializers.IntegerField()
    height = serializers.IntegerField()
    width = serializers.IntegerField()


class StickerPutRequestSerializer(serializers.Serializer):
    sticker_image_url = serializers.URLField()
    xcoor = serializers.IntegerField()
    ycoor = serializers.IntegerField()
    height = serializers.IntegerField()
    width = serializers.IntegerField()
    rotate = serializers.IntegerField()


class DiaryTextBoxPutRequestSerializer(serializers.Serializer):
    diary_id = serializers.IntegerField()
    day = serializers.CharField()
    textboxs = TextBoxPutRequestSerializer()
    stickers = StickerPutRequestSerializer()


class DiaryTextBoxPutResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    

class DiaryStickerRequestSerializer(serializers.Serializer):
    content = serializers.CharField()

class DiaryStickerGetResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))

