import hashlib
import urllib2
import urllib
from urlparse import urlparse

from celery.task import task
from url2feed import extract
from pyfav import download_favicon
from django.conf import settings

from service.models import Website

@task
def get_feed_url(url, callback):
    print url, callback
    result = extract(url)
    resp = urllib2.urlopen(callback, urllib.urlencode(result))
    return result

@task
def get_favicon(url):
    domain = urlparse(url).netloc
    try:
        site = Website.objects.get(domain=domain)
    except Website.DoesNotExist:
        filename = hashlib.md5(domain).hexdigest()
        target_dir = "{}/favicons/".format(settings.MEDIA_ROOT)
        favicon_saved_at = download_favicon(url,
                    file_prefix=filename + "-",
                    target_dir=target_dir)
        site = Website(domain=domain)
        site.favicon.name = favicon_saved_at
        site.save()
    return site.favicon.name
