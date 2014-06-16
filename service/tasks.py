import urllib2

from celery.task import task
from url2feed import extract



@task
def get_feed_url(url, callback):
    result = extract(url)
    urllib2.urlopen(callback, result)
    return result
