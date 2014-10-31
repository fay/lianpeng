import os
import string
import hashlib
import urllib2
import urllib
from urlparse import urlparse

from celery.task import task
import requests
from url2feed import extract
from django.conf import settings

from service.models import Website
from service.scraper import Scraper

@task
def get_feed_url(url, callback):
    print url, callback
    result = extract(url)
    resp = urllib2.urlopen(callback, urllib.urlencode(result))
    return result

def download_favicon(favicon_url, file_prefix='', target_dir='/tmp'):

    if not favicon_url:
        raise Exception("Unable to find favicon for, %s" % url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 \
            Safari/537.36'
    }
    response = requests.get(favicon_url, timeout=20, headers=headers)
    if response.status_code == requests.codes.ok:
        parsed_uri = urlparse(favicon_url)
        favicon_filepath = parsed_uri.path
        favicon_path, favicon_filename  = os.path.split(favicon_filepath)

    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    sanitized_filename = "".join([x if valid_chars \
        else "" for x in favicon_filename])

    sanitized_filename = os.path.join(target_dir, file_prefix +
        sanitized_filename)

    with open(sanitized_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()

    return sanitized_filename

@task
def get_favicon(url):
    scraper = Scraper(url, fields=['domain', 'favicon'])
    result = scraper.scrape()
    domain = result.get('domain')
    favicon_url = result.get('favicon')

    filename = hashlib.md5(domain).hexdigest()
    target_dir = "{}/favicons/".format(settings.MEDIA_ROOT)
    name = settings.STATIC_URL + "img/default_favicon.png"

    site = Website(domain=domain)
    site.favicon.name = name
    site.save()

    try:
        favicon_saved_at = download_favicon(favicon_url,
                    file_prefix=filename + "-",
                    target_dir=target_dir)
        name = favicon_saved_at.split(settings.MEDIA_ROOT)[1]
        if name:
            site.favicon.name = name
            site.save()
    except:
        pass

    return site.favicon.name
