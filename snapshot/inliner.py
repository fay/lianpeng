# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

# TODO
#   * do smart image translation, CSS' often declare background and background-image urls
#       check python-cssutils, if it's of any use. for now it's a naive regexp
#

import sys, re, urllib2, base64, mimetypes, urlparse, os
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from django.conf import settings

#feedparse has a _kick ass_ charset detection function!

def is_remote(address):
    return urlparse.urlparse(address)[0] in ('http', 'https')

def data_encode_image(name, content):
    return u'data:%s;base64,%s' % (mimetypes.guess_type(name)[0],base64.standard_b64encode(content))

def ignore_url(address):
    url_blacklist = ('getsatisfaction.com',
                     'google-analytics.com',)

    for bli in url_blacklist:
        if address.find(bli) != -1:
            return True

    return False

def get_content(from_, expect_binary=False):
    if is_remote(from_):
        if ignore_url(from_):
            return u''

        ct = urllib2.urlopen(from_, timeout=10)
        if not expect_binary:
            s = ct.read()
            return unicode(s, 'utf-8')
        else:
            return ct.read()
    else:
        s = open(from_).read()
        if not expect_binary:
            encodings = feedparser.convert_to_utf8({}, s)
            return unicode(s, encodings[1])
        else:
            return s

def resolve_path(base, target):
    if False:
        return urlparse.urljoin(base, target)

    target = target.replace('"', '').replace("'", '')
    if is_remote(target):
        return target

    if target.startswith('/'):
        if is_remote(base):
            protocol,rest = base.split('://')
            if target.startswith('//'):
                return '%s:%s' % (protocol, target)
            else:
                return '%s://%s%s' % (protocol, rest.split('/')[0],target)
        else:
            return target
    else:
        try:
            base,rest = base.rsplit('/',1)
            return '%s/%s' % (base, target)
        except ValueError:
            return target

def replaceJavascript(base_url, soup):
    for js in soup.findAll('script', {'src': re.compile('.+')}):
        try:
            real_js = get_content(resolve_path(base_url, js['src']))
            js_tag = Tag(soup, 'script')
            js_tag.insert(0, NavigableString(real_js))
            js.replaceWith(js_tag)
        except Exception,e:
            print 'failed to load javascript from %s' % js['src']
            print e

css_url = re.compile(ur'url\((.+?)\)')
def replaceCss(base_url,soup):
    for css in soup.findAll('link', {'rel':'stylesheet', 'href':re.compile('.+')}):
        try:
            real_css = get_content(resolve_path(base_url, css['href']))

            def replacer(result):
                try:
                    path = resolve_path(resolve_path(base_url,css['href']), result.groups()[0])
                    path = path.replace('"', '').replace("'", "")
                    print path
                    return u'url(%s)' % data_encode_image(path,get_content(path, True))
                except Exception, e:
                    print e
                    return u''

            style_tag = Tag(soup, 'style')
            style_tag.insert(0, NavigableString(re.sub(css_url, replacer, real_css)))
            css.replaceWith(style_tag)

        except Exception, e:
            print 'failed to load css from %s' % css['href']
            print e

def replaceImages(base_url, soup):
    from itertools import chain

    for img in chain(soup.findAll('img', {'src': re.compile('.+')}),
                     soup.findAll('input', {'type': 'image', 'src':re.compile('.+')})):
        try:
            path = resolve_path(base_url, img['src'])
            real_img = get_content(path, True)
            img['src'] = data_encode_image(path.lower(), real_img)
        except Exception, e:
            print 'failed to load image from %s' % img['src']
            print e


def snapshot(url):
    bs = BeautifulSoup(get_content(url))

    replaceJavascript(url, bs)
    replaceCss(url, bs)
    replaceImages(url, bs)

    base_tag = Tag(bs, 'base')
    base_tag['target'] = '_blank'
    base_tag['href'] = url
    bs.html.head.insert(0, base_tag)
    return bs

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

