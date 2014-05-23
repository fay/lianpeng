import time
import HTMLParser
import datetime
import sys

from BeautifulSoup import BeautifulSoup
from django.utils.timezone import utc, now
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bookmark.models import Bookmark, List

def import_to_lianpeng(file_name):
    f = open(file_name)
    xml = f.read()
    f.close()
    soup = BeautifulSoup(xml)
    posts = soup.findAll('post')
    #import pdb;pdb.set_trace()
    h = HTMLParser.HTMLParser()
    for post in posts:
        stamp = float(post.createtime.string) / 1000
        created_time = datetime.datetime.utcfromtimestamp(stamp).replace(tzinfo=utc)
        tags = " ".join([tag.string for tag in post.findAll('tag')])
        title = post.find('title').string
        if not title:
            title = "No Title"
        print created_time
        print title
        note = post.find('text')
        if note and note.string:
            note = h.unescape(note.string)
        else:
            note = ""
        bookmark = Bookmark(list_id=1397, user_id=3, title=title, note=note, created_time=created_time, domain='note.lianpeng.me', tags=tags)
        bookmark.save()
        bookmark = Bookmark.objects.get(id=bookmark.id)
        bookmark.url = 'http://lianpeng.me/note/{}/'.format(bookmark.id)
        bookmark.save()


class Command(BaseCommand):

    def handle(self,*args,**options):
        if len(args) < 1:
            print 'please specify the backup xml file '
            return
        file_name = args[0]
        import_to_lianpeng(file_name)
