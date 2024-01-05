from django.db import models
from harucalendar.models import Harucalendar

# Create your models here

class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True)
    calendar_id = models.ForeignKey(Harucalendar,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    diary_date = models.CharField(max_length=10)
    diary_day = models.CharField(max_length=10)
    sns_link = models.URLField(max_length=500)
    diary_bg_url = models.URLField(max_length=500)
    is_expiry = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    #calendar
    # diary_textboxs
    # diary_stickers
    # guests