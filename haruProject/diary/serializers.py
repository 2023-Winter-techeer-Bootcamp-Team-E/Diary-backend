from rest_framework import serializers

from .models import Diary


class DiaryDetailSerializer(serializers.ModelSerializer):
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
        fields = ['sns_link']


class DiaryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['title', 'diary_date', 'diary_day', 'sns_link', 'diary_bg_url']

    def create(self, validated_data):
        return Diary.objects.create(**validated_data)


class DiaryFinalSaveSerializer(serializers.ModelSerializer):
    # diary_textboxs = Diary_textbox_Serializer(many=True)
    # diary_stickers = Diary_sticker_Serializer(many=True)
    class Meta:
        model = Diary
        # textBoxs, stickers

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.diary_date = validated_data.get('diary_date', instance.diary_date)
        instance.diary_day = validated_data.get('diary_day', instance.diary_day)
        instance.sns_link = validated_data.get('sns_link', instance.sns_link)
        instance.diary_bg_url = validated_data.get('diary_bg_url', instance.diary_bg_url)
        instance.save()

        # # Update or create TextBox instances
        # textBoxs_data = validated_data.pop('textBoxs', [])
        # for textBox_data in textBoxs_data:
        #     TextBox.objects.update_or_create(diary=instance, **textBox_data)
        #
        # # Update or create Sticker instances
        # stickers_data = validated_data.pop('stickers', [])
        # for sticker_data in stickers_data:
        #     Sticker.objects.update_or_create(diary=instance, **sticker_data)

        return instance
