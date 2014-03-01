from hashlib import md5

from django.core.files.base import ContentFile
from django.conf import settings

from celery.task import task
from snapshot.inliner import snapshot
from snapshot.models import Snapshot

@task
def create_snapshot_task(bookmark):
    url = bookmark.url
    charset = bookmark.charset
    soup = snapshot(url, charset)
    html = ContentFile(str(soup))
    snapshot_obj = Snapshot(bookmark=bookmark)
    filename = "{}.html".format(bookmark.unique_key)
    snapshot_obj.html_file.save(filename, html)
    snapshot_obj.save()
