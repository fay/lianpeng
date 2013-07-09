import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bookmark.models import List

class Command(BaseCommand):

    def handle(self,*args,**options):
        lists = List.objects.all()
        for l in lists:
            l.count = l.bookmark_set.all().count()
            l.save()

