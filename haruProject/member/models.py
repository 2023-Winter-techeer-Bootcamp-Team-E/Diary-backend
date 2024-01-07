from django.db import models


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=50)
    password = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    '''def __str__(self):
        return self.login_id
                            '''