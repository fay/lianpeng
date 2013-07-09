import json
import re
from BeautifulSoup import BeautifulSoup, SoupStrainer 
import traceback
import urllib
import urllib2
import urlparse
import HTMLParser


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError

from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from harvest.util import *

@csrf_exempt
def index(request):
    data = get_pageinfo(request.POST)
    return HttpResponse(json.dumps(data))

def get_pageinfo(req_data):
    url = req_data.get('url')
    if url.endswith('#'): # delete the last appended #
        url = url[:len(url) - 1]
    data = {'url':url}
    if 'domain' not in req_data:
        url_parts = urlparse.urlparse(url)
        data['domain'] = url_parts.netloc
    if 'title' not in req_data:
        if url :
            try:
                r = urllib2.urlopen(url, timeout=5)
            except Exception, e:
                print traceback.print_exc()
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

                        try:
                            title = soup.head.title.string
                        except Exception:
                            title = 'Untitled'
                        data['title'] = title.strip()

                        metas = soup.findAll('meta', {'name': 'description'})
                        if len(metas) > 0:
                            meta = metas[0]
                            for attr in meta.attrs:
                                if attr[0] == 'content':
                                    description =  attr[1]
                                    data['note'] = description.strip()
    else:
        charset = req_data.get('charset')
        title = req_data.get('title', url)
        note = req_data.get('note', '')

        data['title'] = title
        data['note'] = note
        data['domain'] = req_data.get('domain', '')
    return data

def bookmarklet_js(request):
    return render(request, "harvest/bookmarklet.js", content_type="text/javascript")

@csrf_exempt
def bookmarklet_popup(request):

    data = request.POST or request.GET
    charset = data.get('charset')
    if charset and charset.lower().replace('-', '') != 'utf8':
        request.encoding = data.get('charset')
        data = request.POST or request.GET
    data = get_pageinfo(data)
    context = {}
    context['data'] = data
    if settings.DEBUG:
        post_server = 'http://127.0.0.1:8000'
    else:
        post_server = 'http://lianpeng.me'
    context['post_url'] = post_server + '/api/v1/bookmark/'
    context['login_url'] = post_server + '/accounts/login/'
    context['post_server'] = post_server
    return render(request, "harvest/bookmarklet.html", context)

def save_bookmark(request):
    if settings.DEBUG:
        post_server = 'http://127.0.0.1:8000'
    else:
        post_server = 'http://lianpeng.me'
    data = request.POST
    urllib.urlopen(post_server + '/api/v1/bookmark/', json.dumps(data), {"content_type":"application/json"})
    return 

URL_RE = re.compile("([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}")
def extract_tag(request):
    ''' get tags from url
    '''
    
    url = request.GET.get('url')
    text = ""
    if url :
        try:
            r = urllib2.urlopen(url, timeout=15)
        except Exception, e:
            print traceback.print_exc()
            pass
        else:
            if r.getcode() == 200:
                try:
                    text = r.read()
                except:
                    print traceback.print_exc()
                    pass
                else:
                    #url_parts = urlparse.urlparse(url)
                    #print url_parts
                    # gb18030 is working with both utf-8 and gb2312, see http://leeon.me/a/beautifulsoup-chinese-page-resolve
                    soup = BeautifulSoup(text, fromEncoding="gb18030") 
                    title = soup.html.head.title.string
                    text = title + " " + " ".join([p.text for p in soup('h1')]) + " " + \
                            " ".join([p.text for p in soup('h2')]) + " " + \
                            " ".join([p.text for p in soup('p')]) 
                    keywords = get_meta_content(soup, 'keywords') 
                    text += " " + keywords.strip() * 2
                    html_parser = HTMLParser.HTMLParser()
                    text = html_parser.unescape(text) # decode html entities
                    text = re.sub("https?", "", text).lower()
                    text = URL_RE.sub("", text)

    tags = get_tags(text)
    return HttpResponse(json.dumps(tags))

def get_tags(text):
    from jieba.analyse import extract_tags
    num = 7
    tags = []
    if text:
        tags = [tag for tag in extract_tags(text, 20) if tag[0] not in STOP_WORDS][:num]
    return tags



