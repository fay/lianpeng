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
    filename = hashlib.md5(domain).hexdigest()
    target_dir = "{}/favicons/".format(settings.MEDIA_ROOT)
    name = settings.STATIC_URL + "img/default_favicon.png"
    site = Website(domain=domain)
    site.favicon.name = name
    site.save()
    try:
        favicon_saved_at = download_favicon(url,
                    file_prefix=filename + "-",
                    target_dir=target_dir)
        name = favicon_saved_at.split(settings.MEDIA_ROOT)[1]
        if name:
            site.favicon.name = name
            site.save()
    except:
        pass
    return site.favicon.name
