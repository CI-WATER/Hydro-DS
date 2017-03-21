import os

from django.db import models
from django.contrib.auth.models import User


def get_upload_path(instance, filename):
    filename = os.path.basename(filename)
    if instance.user:
        user_id = str(instance.user.id)
        upload_to = 'data/user_{user_id}/{file_name}'.format(user_id=user_id, file_name=filename)
    else:
        upload_to = 'data/{file_name}'.format(file_name=filename)

    #print('file_name:' + filename)

    return upload_to


# Create your models here.
class UserFile(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    file = models.FileField(upload_to=get_upload_path)


class Job(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    job_description = models.CharField(max_length=255)
    message = models.CharField(max_length=1000, blank=True, null=True)
    is_success = models.BooleanField(blank=True)