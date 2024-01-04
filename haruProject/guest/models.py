from django.db import models

class Guest(models.Model):
    guest_id = models.AutoField(primary_key=True)
    #diary_id = models.ForeignKey(Diary, on_delete=models.CASCADE)
    guest_pw = models.CharField(max_length=4)  # 비밀번호를 문자열로 저장



