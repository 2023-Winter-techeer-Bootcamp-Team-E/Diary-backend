from django.db import models
from member.models import Member


# Create your models here.


class Harucalendar(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name='harucalendar', on_delete=models.CASCADE)
    year_month_day = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class Harucalendarsticker(models.Model):
    calendar_sticker_id = models.AutoField(primary_key=True)
    calendar_id = models.ForeignKey(Harucalendar, on_delete=models.CASCADE)
    sticker_image_url = models.CharField(max_length=500, unique=True)
    xcoor = models.IntegerField()
    ycoor = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    rolate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
