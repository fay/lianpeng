import urllib2
import urllib

from celery.task import task
from url2feed import extract



@task
def get_feed_url(url, callback):
    print url, callback
    result = extract(url)
    resp = urllib2.urlopen(callback, urllib.urlencode(result))
    return result
