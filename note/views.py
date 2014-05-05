#coding: utf-8

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

from bookmark.models import Bookmark, List, LIST_KIND_CHOICES

@login_required
def index(request):
    l, created = List.objects.get_or_create(kind=LIST_KIND_CHOICES.NOTE,
            user=request.user, defaults={"name": _("Note")})
    site = Site.objects.get_current()
    bookmark = Bookmark(url="http://{}/note/empty/".format(site.domain),
            domain="note.lianpeng.me", title="输入标题", note="",
            user=request.user, charset="UTF-8", list=l)
    bookmark.save()
    bookmark.url = 'http://{}{}'.format(site.domain, reverse('note_detail', args=(bookmark.id, )))
    bookmark.save()
    return redirect('note_edit', id=bookmark.id)

def detail(request, id):
    bookmark = get_object_or_404(Bookmark, id=id)

    if bookmark.list.public or bookmark.user == request.user:
        context = {}
        context['bookmark'] = bookmark
        return render(request, 'note/detail.html', context)
    else:
        raise Http404()

@login_required
def edit(request, id):
    bookmark = get_object_or_404(Bookmark, id=id, user=request.user)
    if request.user == bookmark.user:
        context = {}
        context['bookmark'] = bookmark
        return render(request, 'note/edit.html', context)
    else:
        raise Http404()

