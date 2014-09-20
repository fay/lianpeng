import os
import json
from urlparse import urlparse

from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.conf import settings

from service.tasks import get_feed_url, get_favicon
from service.models import Website

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
        domain = urlparse(url).netloc
        try:
            site = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            get_favicon.delay(url)
        else:
            return redirect(settings.MEDIA_URL + site.favicon.url)
        """
        f = open(file_name)
        data = f.read()
        return HttpResponse(data, content_type="image/x-icon")
        """
    return redirect(settings.STATIC_URL + "img/default_favicon.png")

@csrf_exempt
def html2pdf(request):
    url = request.REQUEST.get('url')
    file_name = request.REQUEST.get('filename')
    target_pdf = '%s/pdfs/%s.pdf' % (settings.MEDIA_ROOT, file_name)
    os.system('wkhtmltopdf %s %s' % (url, target_pdf))
    output = open(target_pdf)
    return HttpResponse(output, mimetype='application/pdf')
