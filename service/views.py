import json

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

from service.tasks import get_feed_url, get_favicon

def feed_url(request):
    url = request.GET.get('link')
    callback = request.GET.get('callback')
    data = {}
    if url and callback:
        get_feed_url.delay(url, callback)
    return HttpResponse("ok")

def favicon(request):
    url = request.GET.get('url')
    if url:
        get_favicon(url)
    raise Http404()


