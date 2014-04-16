#coding: utf-8

import datetime
import re
import urllib2
import json
import os
import hashlib
from urlparse import urlparse

from django.utils.timezone import utc, now
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db import transaction
from django.conf import settings

from BeautifulSoup import BeautifulSoup
from celery.task import task

from bookmark.models import List, Bookmark, SyncState
from social_auth.models import UserSocialAuth
from misc.utils import create_email

@task
def sync():
    usas = UserSocialAuth.objects.filter(provider='github')
    for social_auth in usas:
        states = social_auth.user.syncstate_set.all()
        for state in states:
            if state.list:
                _sync_github(social_auth.user, state.list, state)

@task
def new_user_care_7days():
    seven_days_ago = now() - datetime.timedelta(days=7)
    new_users = User.objects.filter(date_joined__year=seven_days_ago.year,
                                   date_joined__month=seven_days_ago.month,
                                   date_joined__day=seven_days_ago.day)
    subject = '莲蓬网现在使用得如何？'
    template = 'misc/emails/user_care_seven_days.txt'
    recipients = [user.email for user in new_users]
    context = {}
    create_email(subject, recipients, template, context)

@task
@transaction.commit_on_success
def sync_github(user, list_name):
    website = 'github'
    state, created = SyncState.objects.get_or_create(user=user, website=website, defaults={"state": 2})
    if not created and state.state == 2: #: avoid duplicate syncronization
        return
    default_list, created = List.objects.get_or_create(name=list_name, user=user, defaults={"public": True})
    _sync_github(user, default_list, state)

def _sync_github(user, default_list, state):
    website = 'github'
    user_social_auth = user.social_auth.get(provider=website)
    github_username = user_social_auth.extra_data['login']
    page = 1
    while True:
        resp = urllib2.urlopen('https://api.github.com/users/' + github_username + '/starred?page=' + str(page))
        data = resp.read()
        items = json.loads(data)
        for item in items:
            url = item['html_url']
            desc = item['description']
            language = item.get('language', '')
            title = item['full_name']
            try:
                #: if one of the github project url is saved before, stop iterating and return.
                Bookmark.objects.get(list=default_list, url=url, user=user)
                return
            except Bookmark.DoesNotExist:
                bookmark = Bookmark(url=url, user=user, note=desc)
                bookmark.domain = urlparse(url).netloc
                bookmark.title = title
                bookmark.list = default_list
                if language:
                    bookmark.tags = language.lower()
                bookmark.save()
        #: if less than 30, there will no more items, stop fetching data from Github
        if len(items) < 30:
            break
        page += 1

    if state.state != 1:
        state.state = 1
        state.list = default_list
        state.save()

@task
def handle_imported_file(data, user, site, list_name):
    soup = BeautifulSoup(data)
    entries = soup.findAll('dt')

    default_list, created = List.objects.get_or_create(name=list_name, user=user)

    for entry in entries:
        link = entry.find('a')
        bookmark = Bookmark()
        l = None
        date = None
        if not link:
            continue
        for attr in link.attrs:
            if attr[0] == 'href':
                bookmark.url = attr[1]
            if attr[0] == 'add_date':
                stamp = int(attr[1])
                scale = len(attr[1]) - 10
                stamp = stamp / pow(10, scale)
                date = datetime.datetime.utcfromtimestamp(stamp).replace(tzinfo=utc)
                bookmark.created_time = date
            if attr[0] == 'tags':
                tags = attr[1].replace(',', ' ')
                bookmark.tags = tags
            if attr[0] == 'list':
                name = attr[1]
                l, created = List.objects.get_or_create(name=name, user=user)

        if site == 'kippt':
            dd = entry.findNext('dd')
            if dd:
                tags = dd.string
                if tags:
                    tags = re.findall('#([^ ]+)', tags)
                    tags = ' '.join(tags)
                    bookmark.tags = tags
        if site == 'google':
            tag_ele = entry.find('h3')
            if tag_ele:
                tag = tag_ele.string
                continue
            else:
                try:
                    existed_bookmark = Bookmark.objects.get(url=bookmark.url, user=user)
                    existed_bookmark.tags = existed_bookmark.tags + " " + tag
                    existed_bookmark.save()
                    continue
                except Bookmark.DoesNotExist:
                    try:
                        bookmark.tags = bookmark.tags + " " + tag
                    except UnboundLocalError:
                        pass
                except:
                    continue
            

        bookmark.domain = urlparse(bookmark.url).netloc
        if l:
            bookmark.list = l
        else:
            bookmark.list = default_list
        bookmark.title = link.string 
        bookmark.user = user
        # we can not have two bookmark with the same url in the same list
        try:
            Bookmark.objects.get(url=bookmark.url, list=bookmark.list)
            continue
        except Bookmark.DoesNotExist:
            pass
        try:
            bookmark.save()
        except:
            continue
