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



class BookmarkModelTest(TestCase):

    fixtures = ['users.json', 'points']

    def setUp(self):
        super(BookmarkModelTest, self).setUp()
        self.user = User.objects.create_user(username="test", email="user@example.com", password="test")
        self.john = User.objects.create_user(username="john", email="user@example.com", password="test")

    def tearDown(self):
        Bookmark.objects.all().delete()

    def test_award_points(self):
        l = self.user.list_set.all()[0] #: Inbox
        bookmark = Bookmark(user=self.user, title="test page", url="http://example.me/", domain='example.com', list=l)
        bookmark.save()
        self.assertTrue(self.user.targetstat_targets.points == 1)

        bookmark = Bookmark(user=self.user, title="test page", url="http://example.com/", domain='example.me', list=l)
        bookmark.save()
        self.assertTrue(self.user.targetstat_targets.points == 1)


