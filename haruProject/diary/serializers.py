from rest_framework import serializers

from .models import Diary, DiaryTextBox, DiarySticker


class DiaryTextBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryTextBox
        fields = ['textbox_id', 'writer', 'content', 'xcoor', 'ycoor', 'width', 'height', 'rotate']


class DiaryStickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiarySticker
        fields = ['sticker_id', 'sticker_image_url', 'xcoor', 'ycoor', 'width', 'height', 'rotate']


class DiaryDetailSerializer(serializers.ModelSerializer):
    diaryTextBoxs = DiaryTextBoxSerializer(many=True, read_only=True)
    diaryStickers = DiaryStickerSerializer(many=True, read_only=True)

    class Meta:
        model = Diary
        exclude = ['is_deleted', 'updated_at']


class DiaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['diary_id', 'is_expiry']
        exclude = ['is_deleted', 'updated_at']


class DiarySnsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['diary_id', 'diary_date', 'sns_link']


class DiaryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['title', 'diary_date', 'diary_day', 'sns_link', 'diary_bg_url']

    def create(self, validated_data):
        return Diary.objects.create(**validated_data)


class DiaryTextBoxCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryTextBox
        fields = ['content']

    def create(self, validated_data):
        return DiaryTextBox.objects.create(**validated_data)


class DiaryStickerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiarySticker
        fields = ['sticker_image_url', 'xcoor', 'ycoor', 'width', 'height', 'rotate']

    def create(self, validated_data):
        return DiarySticker.objects.create(**validated_data)

