from datetime import datetime

from django.db import models
from member.models import Member


# Create your models here.


class Harucalendar(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name='harucalendar', on_delete=models.CASCADE)
    year_month = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class Harucalendarsticker(models.Model):
    calendar_sticker_id = models.AutoField(primary_key=True)
    calendar = models.ForeignKey(Harucalendar, on_delete=models.CASCADE)
    sticker_image_url = models.URLField(max_length=500)
    top = models.IntegerField()
    left = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    rotate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
