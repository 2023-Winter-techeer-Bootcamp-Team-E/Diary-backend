from django.db import models
from harucalendar.models import Harucalendar


# Create your models here

class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True)
    calendar_id = models.ForeignKey(Harucalendar, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    diary_date = models.CharField(max_length=10)
    diary_day = models.CharField(max_length=10)
    sns_link = models.URLField(max_length=500)
    diary_bg_url = models.URLField(max_length=500)
    is_expiry = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class DiaryTextBox(models.Model):
    textbox_id = models.AutoField(primary_key=True)
    diary = models.ForeignKey(Diary, related_name='diaryTextBoxs', on_delete=models.CASCADE)
    writer = models.CharField(max_length=20)
    content = models.TextField()
    xcoor = models.IntegerField()
    ycoor = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    rotate = models.IntegerField()
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(default=False)


class DiarySticker(models.Model):
    sticker_id = models.AutoField(primary_key=True)
    diary = models.ForeignKey(Diary, related_name="diaryStickers", on_delete=models.CASCADE)
    sticker_image_url = models.CharField(max_length=500)
    xcoor = models.IntegerField()
    ycoor = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    rotate = models.IntegerField()
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(default=False)
