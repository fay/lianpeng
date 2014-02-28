from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

from bookmark.models import List
from misc.utils import find_mentions, Choice

DIRECT_BUY = 1
REFERRAL = 2
CHANNEL_CHOICES = ((DIRECT_BUY, 'Direct buy'), (REFERRAL, 'Referral'))

ORDER_STATES = Choice({
        'unpaid': 0,
        'paid': 1,
})

class App(models.Model):

    user = models.ForeignKey(User) #: creator
    name = models.CharField(max_length=16)
    key = models.CharField(max_length=32, unique=True)
    logo = models.URLField()

    lists = models.ManyToManyField(List, through="AppList")

    def __unicode__(self):
        return "{} - {}".format(self.name, self.user)

class AppPlan(models.Model):

    name = models.CharField(max_length=20)
    price = models.IntegerField()
    period = models.PositiveIntegerField(default=30) #default 30 days for a period payment
    app = models.ForeignKey(App)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = (('app', 'price'), )


class UserApp(models.Model):

    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    plan = models.ForeignKey(AppPlan)
    created_time = models.DateTimeField(auto_now_add=True)
    expired_time = models.DateTimeField()
    channel = models.IntegerField(choices=CHANNEL_CHOICES)

    def __unicode__(self):
        return "{} - {}".format(self.app, self.user)

    class Meta:
        unique_together = (("user", "app"), )


class Order(models.Model):

    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    plan = models.ForeignKey(AppPlan)
    price = models.IntegerField()
    amount = models.IntegerField(default=1)
    period = models.PositiveIntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField(choices=ORDER_STATES.to_choices(), default=ORDER_STATES.UNPAID)


class AppList(models.Model):
    app = models.ForeignKey(App)
    list = models.ForeignKey(List)

    class Meta:
        unique_together = (("app", "list"), )

class AppAction(models.Model):
    app = models.ForeignKey(App)
    action = models.CharField(max_length=32)
    link = models.CharField(max_length=128)

