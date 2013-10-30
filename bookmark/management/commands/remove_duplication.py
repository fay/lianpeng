import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bookmark.models import List, Bookmark

class Command(BaseCommand):

    def handle(self,*args,**options):
        list_id = args[0]
        print list_id
        l = List.objects.get(id=list_id)
        user = l.user
        for bookmark in l.bookmark_set.all():
            url = bookmark.url
            duplications = Bookmark.objects.filter(list=l, url=url)[1:]
            print duplications
            for dup in duplications:
                dup.delete()




