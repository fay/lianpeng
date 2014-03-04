"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from market.models import Order, UserApp, App, AppPlan

class MarketTest(TestCase):

    fixtures = ('app', 'plan', 'users')

    def setUp(self):
        self.app = App.objects.get(key='snapshot')
        self.plans = AppPlan.objects.all()
        self.plan1 = self.plans[0]
        self.user = User.objects.get(id=1)

    def test_order(self):
        plan = self.plan1
        app = self.app
        price = plan.price
        amount = 2
        order = Order(price=price, amount=amount, period=plan.period, user=self.user, app=app, plan=plan)
        order.save()
        order.finish()
