"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""


import json
import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.client import Client, ClientHandler
from django.db import close_connection
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


from tastypie.test import ResourceTestCase

from bookmark.models import Bookmark, List, ListInvitation

class BookmarkTest(ResourceTestCase):

    fixtures = ['users.json']

    def setUp(self):
        super(BookmarkTest, self).setUp()
        self.user = User.objects.create_user(username="test", email="user@example.com", password="test")
        self.john = User.objects.create_user(username="john", email="user@example.com", password="test")
        self.client = Client()
        self.post_data = {'title': 'awesome website', 'url': 'http://google.com', 'tags': 'searchengine google'}
        self.factory = RequestFactory()

    def tearDown(self):
        Bookmark.objects.all().delete()

    def get_credentials(self):
        return self.create_basic(username="test", password="test")

    def test_create_default_inbox_list(self):
        user = User.objects.create_user(username="test2", email="test2@example.com", password="test")
        user.save()
        try:
            inbox_list = self.user.list_set.get(kind=0)
            self.assertTrue(inbox_list.kind == 0)
            self.assertTrue(inbox_list.name == 'Inbox')
        except List.DoesNotExist:
            self.fail()

    def test_add_bookmark(self):
        self.assertTrue(len(Bookmark.objects.all()) == 0)
        self.client.login(username="test", password="test")
        response = self.client.post('/api/v1/bookmark/', json.dumps(self.post_data), content_type="application/json")
        self.assertTrue(response.status_code == 201)
        self.assertTrue(len(Bookmark.objects.all()) == 1)

    def test_add_bookmark_with_arbitrary_user(self):
        self.assertTrue(len(Bookmark.objects.all()) == 0)
        self.client.login(username="test", password="test")
        data = self.post_data
        data['user'] = '/api/v1/user/' + str(self.john.id)
        print data
        response = self.client.post('/api/v1/bookmark/', json.dumps(data), content_type="application/json")
        self.assertTrue(response.status_code==201)
        self.assertTrue(len(Bookmark.objects.all()) == 1)
        b = Bookmark.objects.all()[0]
        self.assertTrue(b.user.id ==self.user.id)

    def test_add_bookmark_with_arbitrary_user_id(self):
        self.assertTrue(len(Bookmark.objects.all()) == 0)
        self.client.login(username="test", password="test")
        data = self.post_data
        data['user'] = self.john.id
        response = self.client.post('/api/v1/bookmark/', json.dumps(data), content_type="application/json")
        self.assertTrue(response.status_code==201)
        self.assertTrue(len(Bookmark.objects.all()) == 1)
        b = Bookmark.objects.all()[0]
        self.assertTrue(b.user.id == self.user.id)

    def test_get_bookmark(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        response = self.client.get('/api/v1/bookmark/'+ str(bookmark.id), content_type="application/json")
        print response.status_code
        data = json.loads(response.content)
        self.assertTrue(bookmark.id == data['id'])

    def test_get_others_bookmarks(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        l = List.objects.get(name="Inbox", user=self.user)
        self.client.login(username="john", password="test")
        response = self.client.get('/api/v1/list/' + str(l.id) + '/bookmarks', content_type="application/json")
        print response
        print response.status_code
        data = json.loads(response.content)
        self.assertTrue(len(data['objects']) == 0)

    def test_get_others_bookmark(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="john", password="test")
        response = self.client.get('/api/v1/bookmark/'+ str(bookmark.id), content_type="application/json")
        print response.status_code
        self.assertTrue(response.status_code == 401)

    def test_edit_bookmark(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        put_data = {'title': 'awesome website', 'url': 'http://google.com', 'tags': 'searchengine google', 'created_time': "2013-2-12"}
        response = self.client.put('/api/v1/bookmark/'+ str(bookmark.id), json.dumps(put_data), content_type="application/json")
        print response.status_code
        self.assertTrue(response.status_code == 202)
        bookmark = Bookmark.objects.get(id=bookmark.id)
        self.assertTrue(bookmark.title == "awesome website")

    def test_change_bookmark_list(self):
        l = List(name="My List", user=self.user)
        l.save()
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        put_data = {'title': 'awesome website', 'url': 'http://google.com', 'list': '/api/v1/list/' + str(l.id) , 'tags': 'searchengine google', 'created_time': "2013-2-12"}
        response = self.client.put('/api/v1/bookmark/'+ str(bookmark.id), json.dumps(put_data), content_type="application/json")
        self.assertTrue(response.status_code == 202)
        bookmark = Bookmark.objects.get(id=bookmark.id)
        self.assertTrue(bookmark.title == "awesome website")

    def test_change_bookmark_list_that_is_not_mine(self):
        l = List(name="My List", user=self.john)
        l.save()
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        put_data = {'title': 'awesome website', 'url': 'http://google.com', 'list': '/api/v1/list/' + str(l.id) , 'tags': 'searchengine google', 'created_time': "2013-2-12"}
        response = self.client.put('/api/v1/bookmark/'+ str(bookmark.id), json.dumps(put_data), content_type="application/json")
        self.assertTrue(response.status_code == 401)

    def test_edit_bookmark_no_domain_change(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        put_data = {'title': 'awesome website', 'url': 'http://google.com', 'domain':'baidu.com', 'tags': 'searchengine google', 'created_time': "2013-2-12"}
        response = self.client.put('/api/v1/bookmark/'+ str(bookmark.id), json.dumps(put_data), content_type="application/json")
        print response.status_code
        self.assertTrue(response.status_code == 202)
        bookmark = Bookmark.objects.get(id=bookmark.id)
        self.assertTrue(bookmark.title == "awesome website")
        print bookmark.domain
        self.assertTrue(bookmark.domain == "google.com")

    def test_edit_bookmark_without_permission(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        user = User.objects.create_user(username="test2", email="test2@example.com", password="test")
        user.save()
        self.client.login(username="test2", password="test")
        put_data = {'title': 'awesome website', 'url': 'http://google.com', 'tags': 'searchengine google', 'created_time': "2013-2-12"}
        response = self.client.put('/api/v1/bookmark/'+ str(bookmark.id), json.dumps(put_data), content_type="application/json")
        self.assertTrue(response.status_code == 401)
        bookmark = Bookmark.objects.get(id=bookmark.id)
        self.assertTrue(bookmark.title == "you cannot edit me")

    def test_delete_bookmark(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="test", password="test")
        response = self.client.delete('/api/v1/bookmark/'+ str(bookmark.id), content_type="application/json")
        print response, response.status_code
        self.assertTrue(response.status_code == 204)
        try:
            bookmark = Bookmark.objects.get(id=bookmark.id)
            self.fail()
        except:
            pass

    def test_delete_bookmark_by_other_user(self):
        bookmark = Bookmark(user=self.user, title="you cannot edit me", url="http://google.com", domain="google.com")
        bookmark.save()
        self.client.login(username="john", password="test")
        response = self.client.delete('/api/v1/bookmark/'+ str(bookmark.id), content_type="application/json")
        print response, response.status_code
        self.assertTrue(response.status_code == 401)
        try:
            bookmark = Bookmark.objects.get(id=bookmark.id)
        except:
            self.fail()

    def test_create_list(self):
        self.client.login(username="test", password="test")
        list_data = {'name': 'My List'}
        response = self.client.post('/api/v1/list/', json.dumps(list_data), content_type="application/json")
        print response
        try:
            my_list = self.user.list_set.get(name="My List")
            self.assertTrue(my_list.kind == 2)
        except List.DoesNotExist:
            self.fail()

    def test_change_list_user(self):
        l = List(name="My List", user=self.user)
        l.save()
        self.client.login(username="test", password="test")
        list_data = {'name': 'My List2', 'user': '/api/v1/user/' + str(self.john.id)}
        response = self.client.post('/api/v1/list/', json.dumps(list_data), content_type="application/json")
        print response
        try:
            my_list = self.user.list_set.get(name="My List")
            self.assertTrue(my_list.user == self.user)
        except List.DoesNotExist:
            self.fail()

    def test_create_list_for_other_user(self):
        self.client.login(username="test", password="test")
        list_data = {'name': 'My List2', 'user': '/api/v1/user/' + str(self.john.id)}
        response = self.client.post('/api/v1/list/', json.dumps(list_data), content_type="application/json")
        print response
        try:
            my_list = self.user.list_set.get(name="My List2")
            self.assertTrue(my_list.kind == 2)
            self.assertTrue(my_list.user == self.user)
        except List.DoesNotExist:
            self.fail()

    def test_delete_sys_list(self):
        self.client.login(username="test", password="test")
        inbox_list = self.user.list_set.get(kind=0)
        response = self.client.delete('/api/v1/list/'+ str(inbox_list.id), content_type="application/json")
        try:
            inbox_list = self.user.list_set.get(kind=0)
            self.assertTrue(inbox_list.kind == 0)
        except List.DoesNotExist:
            self.fail()

    def test_delete_list(self):
        l = List(name="My List", user=self.user)
        l.save()
        self.client.login(username="test", password="test")
        response = self.client.delete('/api/v1/list/'+ str(l.id), content_type="application/json")
        try:
            inbox_list = self.user.list_set.get(name="My List")
            self.fail()
        except List.DoesNotExist:
            pass

    def test_delete_list_by_other_user(self):
        l = List(name="My List", user=self.user)
        l.save()
        self.client.login(username="john", password="test")
        response = self.client.delete('/api/v1/list/'+ str(l.id), content_type="application/json")
        try:
            inbox_list = self.user.list_set.get(name="My List")
        except List.DoesNotExist:
            self.fail()

    def test_get_list(self):
        l = List(name="My List", user=self.user)
        l.save()
        self.client.login(username="test", password="test")
        response = self.client.get('/api/v1/list/'+ str(l.id), content_type="application/json")
        print response
        data = json.loads(response.content)
        self.assertTrue(data['id'] == l.id)
        
    def test_get_others_list(self):
        l = List(name="My List", user=self.user)
        l.save()
        self.client.login(username="john", password="test")
        response = self.client.get('/api/v1/list/'+ str(l.id), content_type="application/json")
        print response
        self.assertTrue(response.status_code == 401)

    def test_create_list_invitation(self):
        self.client.login(username="test", password="test")
        l = List.objects.get(name="Inbox", user=self.user)
        post_data = {'invitee': 'john', 'list': '/api/v1/list/' + str(l.id), 'permission': 'can_view'}
        response = self.client.post('/api/v1/listinvitation/', json.dumps(post_data), content_type="application/json")
        print response
        data = json.loads(response.content)
        self.assertTrue(data['id'] > 0)
        self.client.login(username="john", password="test")
        response = self.client.get('/list/accept/' + str(data['id']) + '/')
        self.assertTrue(self.john.has_perm('can_view', l))

    def test_create_list_invitation_with_other_user(self):
        self.client.login(username="test", password="test")
        l = List.objects.get(name="Inbox", user=self.user)
        post_data = {'invitee': 'john', 'list': '/api/v1/list/' + str(l.id), 
                     'permission': 'can_view', 
                     'user': '/api/v1/user/' + str(self.john.id)}
        response = self.client.post('/api/v1/listinvitation/', json.dumps(post_data), content_type="application/json")
        print response
        print response.status_code
        data = json.loads(response.content)
        list_invitation = ListInvitation.objects.get(id=data['id'])
        self.assertTrue(list_invitation.user == self.user)

    def test_edit_list_invitation(self):
        l = List.objects.get(name="Inbox", user=self.user)
        list_invitation = ListInvitation(list=l, user=self.user, invitee='john', permission="can_view")
        list_invitation.save()

        self.client.login(username="test", password="test")
        post_data = {'invitee': 'john', 'list': '/api/v1/list/' + str(l.id), 'permission':"can_edit"}
        response = self.client.put('/api/v1/listinvitation/' + str(list_invitation.id), json.dumps(post_data), content_type="application/json")
        print response
        data = json.loads(response.content)
        self.assertTrue(data['permission'] == 'can_edit')
        self.assertTrue(self.john.has_perm('can_edit', l))

    def test_get_list_invitation(self):
        l = List.objects.get(name="Inbox", user=self.user)
        list_invitation = ListInvitation(list=l, user=self.user, invitee='john', permission="can_view")
        list_invitation.save()

        self.client.login(username="test", password="test")
        response = self.client.get('/api/v1/listinvitation/' + str(list_invitation.id), content_type="application/json")
        print response
        data = json.loads(response.content)
        self.assertTrue(data['id'] == list_invitation.id)

    def test_get_others_list_invitation(self):
        l = List.objects.get(name="Inbox", user=self.user)
        list_invitation = ListInvitation(list=l, user=self.user, invitee='john', permission="can_view")
        list_invitation.save()

        self.client.login(username="john", password="test")
        response = self.client.get('/api/v1/listinvitation/' + str(list_invitation.id), content_type="application/json")
        print response
        self.assertTrue(response.status_code == 401)
