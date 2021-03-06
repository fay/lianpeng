import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.utils.translation import ugettext as _
from django.utils import timezone

from bookmark.models import List
from misc.utils import find_mentions, Choice

CHANNEL_CHOICES = Choice(('DIRECT_BUY', 1, "Direct buy"), ('REFERRAL', 2, 'Referral'))

ORDER_STATES = Choice(
        ('UNPAID', 0, _('unpaid')),
        ('PAID', 1, _('paid')),
)

class UserAppManager(models.Manager):

    def is_active(self, user, app_key):
        try:
            user_app = self.get(user=user, app__key=app_key)
            if user_app.is_expired():
                return False
            return user_app
        except UserApp.DoesNotExist:
            return False

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
    channel = models.IntegerField(choices=CHANNEL_CHOICES,
            default=CHANNEL_CHOICES.DIRECT_BUY)

    objects = UserAppManager()

    def is_expired(self):
        return timezone.now() > self.expired_time

    def status_display(self):
        if self.is_expired():
            return _("Expired")
        else:
            if (self.expired_time - timezone.now()).days <= 7:
                return _("Going to expired")
            return _("In Use")

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
    state = models.IntegerField(choices=ORDER_STATES,
            default=ORDER_STATES.UNPAID)
    trade_status = models.CharField(max_length=32, default="INIT")

    @property
    def total_fees(self):
        return self.price * self.amount

    @property
    def days(self):
        return self.amount * self.period

    def is_paid(self):
        return self.state == ORDER_STATES.PAID

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
        now = timezone.now()
        try:
            user_app = UserApp.objects.get(user=self.user, app=self.app)
        except UserApp.DoesNotExist:
            #: user purchase app for the first time
            start_time = now
            user_app = UserApp(user=self.user, app=self.app)
        else:
            #: user bought the app before
            start_time = user_app.expired_time
            if start_time < now: #: expired already
                start_time = now

        expired_time = start_time + datetime.timedelta(
                days=self.plan.period * self.amount)

        user_app.plan = self.plan
        user_app.expired_time = expired_time
        user_app.save()

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

