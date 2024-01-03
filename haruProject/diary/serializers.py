from rest_framework import serializers

from .models import Diary


class DiaryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        exclude = ['deleted_at', 'updated_at']


class DiaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['diary_id', 'is_expiry']
        exclude = ['deleted_at', 'updated_at']


class DiarySnsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['sns_link']


class DiaryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['title', 'diary_date', 'diary_day', 'sns_link', 'diary_bg_url']
        exclude = ['deleted_at', 'updated_at']


class DiaryFinalSaveSerializer(serializers.ModelSerializer):
    # diary_textboxs = Diary_textbox_Serializer(many=True)
    # diary_stickers = Diary_sticker_Serializer(many=True)
    class Meta:
        model = Diary
        fields = ['diary_date', 'diary_day']
        # textBoxs, stickers