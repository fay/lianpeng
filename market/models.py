import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.utils.translation import ugettext as _

from bookmark.models import List
from misc.utils import find_mentions, Choice

CHANNEL_CHOICES = Choice({'direct_buy': 1, 'referral': 2})

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

    @property
    def unit(self):
        if self.period == 30:
            return _("month")
        elif self.period == 365:
            return _("year")
        else:
            return _("days")

    class Meta:
        unique_together = (('app', 'price'), )


class UserApp(models.Model):

    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    plan = models.ForeignKey(AppPlan)
    created_time = models.DateTimeField(auto_now_add=True)
    expired_time = models.DateTimeField()
    channel = models.IntegerField(choices=CHANNEL_CHOICES.to_choices(),
            default=CHANNEL_CHOICES.DIRECT_BUY)

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
    state = models.IntegerField(choices=ORDER_STATES.to_choices(),
            default=ORDER_STATES.UNPAID)
    trade_status = models.CharField(max_length=32, default="INIT")

    def finish(self):
        #: basic test
        if self.state == ORDER_STATES.PAID:
            return

        #: concurrency test
        #: one order can only be finished once, if more than one,
        #: there will be an IntegrityError raised
        OrderLock(order=self).save()

        self.state = ORDER_STATES.PAID
        self.save()
        now = datetime.datetime.now()
        expired_time = now + datetime.timedelta(
                days=self.plan.period * self.amount)
        userapp, created = UserApp.objects.get_or_create(
                user=self.user,
                app=self.app,
                defaults={'expired_time': expired_time, 'plan': self.plan})

class OrderLock(models.Model):
    """
        prevent the order to be paid more than once
    """
    order = models.OneToOneField(Order)
    created_time = models.DateTimeField(auto_now_add=True)

class AppList(models.Model):
    app = models.ForeignKey(App)
    list = models.ForeignKey(List)

    class Meta:
        unique_together = (("app", "list"), )

class AppAction(models.Model):
    app = models.ForeignKey(App)
    action = models.CharField(max_length=32)
    link = models.CharField(max_length=128)

