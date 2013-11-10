from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

from bookmark.models import List

class App(models.Model):
    user = models.ForeignKey(User) #: creator
    name = models.CharField(max_length=16)
    key = models.CharField(max_length=32, unique=True)
    logo = models.URLField()

    lists = models.ManyToManyField(List, through="AppList")

    def __unicode__(self):
        return "{} - {}".format(self.name, self.user)

class UserApp(models.Model):
    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    created_time = models.DateTimeField(auto_now_add=True)
    expired_time = models.DateTimeField()

    def __unicode__(self):
        return "{} - {}".format(self.app, self.user)

    class Meta:
        unique_together = (("user", "app"), )

class AppList(models.Model):
    app = models.ForeignKey(App)
    list = models.ForeignKey(List)

    class Meta:
        unique_together = (("app", "list"), )

class AppAction(models.Model):
    app = models.ForeignKey(App)
    action = models.CharField(max_length=32)
    link = models.CharField(max_length=128)

