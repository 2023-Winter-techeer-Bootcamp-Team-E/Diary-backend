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
        exclude = ['year_month', 'day', 'title', 'sns_link', 'diary_bg_url', 'created_at']



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
        fields = ['diary_id','year_month','day', 'title','sns_link', 'diary_bg_url','created_at', 'updated_at']


    def create(self, validated_data):
        return Diary.objects.create(**validated_data)


class DiaryTextBoxCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryTextBox
        fields = ['textbox_id', 'writer', 'content', 'xcoor', 'ycoor', 'width', 'height', 'rotate','content']

    def create(self, validated_data):
        return DiaryTextBox.objects.create(**validated_data)


class DiaryStickerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiarySticker
        fields = ['sticker_image_url', 'xcoor', 'ycoor', 'width', 'height', 'rotate']

    def create(self, validated_data):
        return DiarySticker.objects.create(**validated_data)



class DiaryShowserializer(serializers.ModelSerializer):

    class Meta:
        model = Diary
        field = ['diary_id', 'is_expiry', 'diary_day', 'created_at', 'is_expired']

class DiaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['sns_link']

    def update(self, instance, validated_data):
        instance.sns_link = validated_data.get('sns_link', instance.sns_link)
        instance.save()
        return instance


