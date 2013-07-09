import re
import datetime
from urlparse import urlparse

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
from django.contrib import messages
from django.conf import settings

from BeautifulSoup import BeautifulSoup
from guardian.shortcuts import assign_perm
from account.models import EmailAddress

from bookmark.forms import ImportForm, FeedbackForm
from bookmark.models import List, Bookmark, PickedList, ListInvitation
from bookmark.tasks import handle_imported_file

def index(request, username=None, id=None, query=None, tag=None):
    user = request.user
    if user.is_authenticated():
        try:
            email = EmailAddress.objects.get(user=user, email=user.email)
            verified = email.verified 
        except EmailAddress.DoesNotExist:
            verified = False
        today = datetime.date.today()
        if not verified and (today - user.date_joined.date()).days >= \
           settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED_DAYS:
            messages.error(request, _("You need to verify your email address to continue to use Lianpeng.You can check your email inbox.")) 
            return redirect('account_settings')
        context = {}
        return render(request, 'bookmark/index.html', context)
    else:
        return render(request, "homepage.html")

def explore(request):
    filter = request.GET.get('filter')
    context = {}
    if not filter:
        filter = 'stream'
    context['filter'] = filter
    if filter:
        lists = List.objects.filter(public=True).order_by('-created_time')
        list_ids = [l.id for l in lists]
        if filter == 'stream':
            bookmarks = Bookmark.objects.filter(list__id__in=list_ids).order_by('-created_time')
            context['bookmarks'] = bookmarks
        elif filter == 'recent':
            context['lists'] = lists
    else:
        list_ids = PickedList.objects.all().values_list('list_id', flat=True) 
        lists = List.objects.filter(public=True, id__in=list_ids).order_by('-created_time')
        context['lists'] = lists
    return render(request, 'bookmark/explore.html', context)

def list_detail(request, id):
    l = get_object_or_404(List, id=id)
    user = request.user
    invitation = None
    if user.is_authenticated():
        try:
            invitation = ListInvitation.objects.get(list=l, invitee=user.username, status__in=(0, 1))
        except ListInvitation.DoesNotExist:
            pass
    if not l.public and not invitation: 
        return Http404()
    context = {}
    context['list'] = l
    context['bookmarks'] = l.bookmark_set.order_by('-created_time')
    return render(request, 'bookmark/list_detail.html', context)

def bookmark_detail(request, id):
    bookmark = get_object_or_404(Bookmark, id=id, list__public=True)
    context = {}
    context['bookmark'] = bookmark
    return render(request, 'bookmark/bookmark_detail.html', context)

def public_profile(request, username):
    context = {}
    current_user = get_object_or_404(User, username=username)
    lists = List.objects.filter(public=True, user=current_user).order_by('-created_time')
    list_ids = [l.id for l in lists]
    bookmarks = Bookmark.objects.filter(list__id__in=list_ids).order_by('-created_time')
    context['bookmarks'] = bookmarks
    context['lists'] = lists
    context['current_user'] = current_user
    return render(request, 'bookmark/profile.html', context)

@login_required
def import_to(request):
    if request.method == 'GET':
        context = {}
        delicious_form = ImportForm()
        context['import_form'] = delicious_form
        return render(request, 'bookmark/import.html', context)
    else:
        user = request.user
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                site = form.cleaned_data.get('site')
                f = request.FILES['file']
                data = f.read() 
                handle_imported_file.delay(data, user, site)
                messages.info(request, 
                              _("Upload successfully, \
                                we will import your bookmarks to your account \
                                in background.Please wait a minute."))
        return redirect('bookmark_import')

def feedback(request):
    form = FeedbackForm()
    context = {}
    context['form'] = form
    return render(request, "bookmark/feedback.html", context)

@login_required
def list_accept_invitation(request, id):
    user = request.user
    invitation = get_object_or_404(ListInvitation, id=id, invitee=user.username)
    invitation.status = 1
    invitation.save()
    assign_perm(invitation.permission, user, invitation.list)
    return redirect('notifications:all')

@login_required
def list_ignore_invitation(request, id):
    invitation = get_object_or_404(ListInvitation, id=id, invitee=user.username)
    invitation.status = 2
    invitation.save()
    return redirect('notifications:all')
