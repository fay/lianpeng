#coding: utf-8

import datetime
import re
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup
from celery.task import task
from django.utils.timezone import utc
from django.utils.translation import ugettext as _

from bookmark.models import List, Bookmark

@task
def handle_imported_file(data, user, site):
    soup = BeautifulSoup(data)
    entries = soup.findAll('dt')
    if site == 'chrome':
        list_name = _("Export from Chrome Browser ")
    elif site == 'kippt':
        list_name = _('Export from Kippt')
    elif site == 'delicious':
        list_name = _('Export from Delicious')
    elif site == 'google':
        list_name = _('Export from Google Bookmarks')
    else:
        return Http404()

    default_list, created = List.objects.get_or_create(name=list_name, user=user)

    for entry in entries:
        link = entry.find('a')
        bookmark = Bookmark()
        l = None
        date = None
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
                    bookmark.tags = bookmark.tags + " " + tag
                except:
                    continue
            

        bookmark.domain = urlparse(bookmark.url).netloc
        if l:
            bookmark.list = l
        else:
            bookmark.list = default_list
        bookmark.title = link.string 
        bookmark.user = user
        try:
            bookmark.save()
        except:
            continue
            

