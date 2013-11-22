from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Lock(models.Model):
    key = models.CharField(max_length=32, unique=True)
    action = models.CharField(max_length=32, choices=(("award_daily_points", "award_daily_points"), ))
    user = models.ForeignKey(User)
    created_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{} - {}".format(self.user, self.action)

class UserGuide(models.Model):
    user = models.OneToOneField(User)
    finished = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
