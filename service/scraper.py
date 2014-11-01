import os
import requests
import json
import re
from bs4 import BeautifulSoup, SoupStrainer
import traceback
import urllib
import urllib2
import urlparse
import HTMLParser
from hashlib import md5
from selenium import webdriver

from django.conf import settings

class Scraper(object):

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.122 Safari/537.36"}

    def __init__(self, url, fields=None):
        self.url = url
        self.url_parts = urlparse.urlparse(self.url)
        if fields:
            self.fields = fields
        else:
            self.fields = ['domain', 'title', 'description', 'favicon', 'screenshot']

    def scrape(self):
        fields = self.fields
        resp = self.fetch()
        charset = self.parse_charset(resp)
        content = resp.content
        html = content.decode(charset)
        dom = self.parse(html)

        result = {}

        if 'charset' in fields:
            result['charset'] = charset
        if 'domain' in fields:
            domain = self.parse_domain()
            result['domain'] = domain
        if 'title' in fields:
            title = self.parse_title(dom)
            result['title'] = title
        if 'description' in fields:
            desc = self.parse_description(dom)
            result['description'] = desc
        if 'favicon' in fields:
            favicon = self.parse_favicon(dom)
            result['favicon'] = favicon
        if 'screenshot' in fields:
            screenshot = self.screenshot()
            result['screenshot'] = screenshot
        return result

    def parse(self, html):
        strainer = SoupStrainer('head')
        soup = BeautifulSoup(html, parse_only=strainer) 
        return soup

    def parse_title(self, soup):
        try:
            title = soup.head.title.string
        except Exception:
            title = self.url
        title = title.strip()
        return title

    def parse_description(self, soup):
        metas = soup.findAll('meta', {'name': 'description'})
        desc = ''
        if len(metas) > 0:
            meta = metas[0]
            desc = meta.attrs.get('content').strip()
        return desc

    def parse_favicon(self, soup):
        url_parts = self.url_parts
        icon_link = soup.find('link', rel='icon')
        if icon_link and icon_link.has_attr('href'):
            favicon_url = icon_link['href']
            # Sometimes we get a protocol-relative path
            if favicon_url.startswith('//'):
                favicon_url = url_parts.scheme + ':' + favicon_url

            # An absolute path relative to the domain
            elif favicon_url.startswith('/'):
                favicon_url = url_parts.scheme + '://' + \
                    url_parts.netloc + favicon_url
            # A relative path favicon
            elif not favicon_url.startswith('http'):
                path, filename  = os.path.split(url_parts.path)
                favicon_url = url_parts.scheme + '://' + \
                    url_parts.netloc + '/' + os.path.join(path, favicon_url)
            # We found a favicon in the markup and we've formatted the URL
            # so that it can be loaded independently of the rest of the page
            return favicon_url
        favicon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(\
            uri=url_parts)
        response = requests.get(favicon_url, headers=self.headers)
        if response.status_code == requests.codes.ok:
            return favicon_url
        return None

    def parse_charset(self, response):
        if hasattr(self, 'charset'):
            charset = getattr(self, 'charset')
        else:
            charset = 'UTF-8'
            lines = response.content.splitlines(False)
            for line in lines:
                line = line.lower()
                if line.find('charset') >= 0:
                    result = re.findall('charset="?([\w\d-]+)"', line)
                    if result:
                        charset = result[0]
                    break
            if not charset:
                parts = response.headers.get('content-type', 'text/html;charset=UTF-8').split("=")
                if len(parts) >= 2:
                    charset = parts[1].strip()
        #: use gbk instead to prevent some encoding error because gbk is superset of gb2312
        if charset.lower() == 'gb2312':
            charset = 'gbk'
        return charset

    def screenshot(self):
        key = "o-" + md5("%s%s" % (settings.SCREENSHOT_SALT, self.url.decode('utf-8'), )).hexdigest()
        target = "{}/screenshots/{}.png".format(settings.MEDIA_ROOT, key)
        if not os.path.exists(target):
            driver = webdriver.PhantomJS() # or add to your PATH
            driver.set_window_size(1024, 800) # optional
            driver.set_page_load_timeout(60)
            driver.get(self.url)
            driver.save_screenshot(target) # save a screenshot to disk
            driver.quit()
        url = "http://lianpeng.me" + settings.MEDIA_URL + target.split(settings.MEDIA_ROOT + "/")[1]
        return url


    def fetch(self):
        resp = requests.get(self.url, headers=self.headers)
        return resp

    def parse_domain(self):
        return self.url_parts.netloc

if __name__ == '__main__':
    scraper = Scraper('http://lianpeng.me/toozoofoo/list/all')
    scraper.scrape()
