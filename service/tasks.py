import hashlib
import urllib2

from celery.task import task
from url2feed import extract
from pyfav import download_favicon
from django.conf import settings

@task
def get_feed_url(url, callback):
    result = extract(url)
    urllib2.urlopen(callback, result)
    return result

@task
def get_favicon(url):
    filename = hashlib.md5(url).hexdigest()
    target_dir = "{}/favicons/".format(settings.MEDIA_ROOT)
    favicon_saved_at = download_favicon(url,
                file_prefix=filename + "-",
                target_dir=target_dir)
    print favicon_saved_at

