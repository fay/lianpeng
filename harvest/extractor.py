import urllib2
import urlparse

import json
from BeautifulSoup import BeautifulSoup, SoupStrainer 

def get_pagemeta(url, defaults={"title":"", "description":""}, timeout=5):
    data = {}
    if defaults and isinstance(defaults, dict):
        data.update(defaults)
    if url:
        try:
            r = urllib2.urlopen(url, timeout=timeout)
        except Exception, e:
            pass
        else:
            if r.getcode() == 200:
                try:
                    text = r.read()
                except:
                    pass
                else:
                    strainer = SoupStrainer('head')
                    # gb18030 is working with both utf-8 and gb2312, see http://leeon.me/a/beautifulsoup-chinese-page-resolve
                    soup = BeautifulSoup(text, parseOnlyThese=strainer, fromEncoding="gb18030") 
                    title = get_title(soup)
                    if title:
                        data['title'] = title
                    data.update(get_metas(soup))
                    favicon = get_favicon(soup)
                    data['favicon'] = favicon

    return data

def get_title(soup):
    try:
        title = soup.head.title.string.strip()
    except Exception:
        title = None
    return title

def get_favicon(soup):
    links = soup.findAll('link')
    favicon = ""
    for link in links:
        if link.has_key('rel') and "icon" in link['rel'].lower().split(" "):
            favicon = link['href']
            break
    if not favicon:
        url_parts = urlparse.urlparse(url)
        favicon = "{}://{}/favicon.ico".format(url_parts.scheme, url_parts.netloc)
    return favicon

def get_metas(soup):
    metas = soup.findAll('meta')
    meta_dict = {}
    for meta in metas:
        content = ""
        name = ""
        for attr in meta.attrs:
            value = attr[1].strip()
            if attr[0].lower() == 'content':
                content = value
            elif attr[0].lower() == 'name':
                name = value
        if name:
            meta_dict[name] = content
    return meta_dict

