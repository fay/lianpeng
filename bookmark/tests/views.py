import json
import datetime
import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.client import Client, ClientHandler
from django.db import close_connection
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


from tastypie.test import ResourceTestCase

from bookmark.models import Bookmark, List



class BookmarkViewTest(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        super(BookmarkViewTest, self).setUp()
        self.user = User.objects.create_user(username="test", email="user@example.com", password="test")
        self.john = User.objects.create_user(username="john", email="user@example.com", password="test")
        self.client = Client()
        self.post_data = {'title': 'awesome website', 'url': 'http://google.com', 'tags': 'searchengine google'}
        self.factory = RequestFactory()

    def tearDown(self):
        Bookmark.objects.all().delete()

    def test_import(self):
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        with open(os.path.join(ROOT, 'tests/kippt.html')) as fp:
            self.client.login(username="test", password="test")
            r = self.client.post('/import/', {'site': 'kippt', 'file': fp})
        count = Bookmark.objects.count()
        print count
        self.assertTrue(count == 15)
        self.assertTrue(List.objects.filter(user=self.user).count() == 3)
