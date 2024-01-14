from django.db import models
from harucalendar.models import Harucalendar


# Create your models here

class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True)
    calendar = models.ForeignKey(Harucalendar, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    year_month = models.CharField(max_length=10)
    day = models.CharField(max_length=10)
    sns_link = models.CharField(max_length=500)
    diary_bg_url = models.URLField()
    is_expiry = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class DiaryTextBox(models.Model):
    textbox_id = models.AutoField(primary_key=True)
    diary = models.ForeignKey(Diary, related_name='diaryTextBoxs', on_delete=models.CASCADE)
    writer = models.CharField(max_length=20)
    content = models.TextField()
    xcoor = models.IntegerField(blank=True,null=True)
    ycoor = models.IntegerField(blank=True,null=True)
    width = models.IntegerField(blank=True,null=True)
    height = models.IntegerField(blank=True,null=True)
    rotate = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class DiarySticker(models.Model):
    sticker_id = models.AutoField(primary_key=True)
    diary = models.ForeignKey(Diary, related_name="diaryStickers", on_delete=models.CASCADE)
    sticker_image_url = models.URLField(max_length=500)
    xcoor = models.IntegerField(blank=True,null=True)
    ycoor = models.IntegerField(blank=True,null=True)
    width = models.IntegerField(blank=True,null=True)
    height = models.IntegerField(blank=True,null=True)
    rotate = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
