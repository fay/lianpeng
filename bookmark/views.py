import re
import datetime
import calendar
from urlparse import urlparse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache

from BeautifulSoup import BeautifulSoup
from guardian.shortcuts import assign_perm
from account.models import EmailAddress

from bookmark.forms import ImportForm, FeedbackForm
from bookmark.models import List, Bookmark, PickedList, ListInvitation,\
        SyncState, LIST_KIND_CHOICES
from bookmark.tasks import handle_imported_file, sync_github
from misc.models import UserTour

def index(request, username=None, id=None, query=None, tag=None):
    user = request.user
    if 'redirect_to' in request.session:
        redirect_url = request.session['redirect_to']
        del request.session['redirect_to']
        return redirect(redirect_url)
    if user.is_authenticated():
        try:
            email = EmailAddress.objects.get(user=user, email=user.email)
            verified = email.verified 
        except EmailAddress.DoesNotExist:
            verified = False
        today = datetime.date.today()
        if not verified and (today - user.date_joined.date()).days >= \
           settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED_DAYS:
            resend_url = reverse('resend_email_confirmation')
            messages.error(request, _("You need to verify your email address to continue to use Lianpeng.You can check your email inbox. You can also <a href='%s'>resend email confirmation</a>.") % (resend_url,)) 
            return redirect('account_settings')
        context = {}
        user_tour, created = UserTour.objects.get_or_create(user=user)
        context['user_tour'] = user_tour
        return render(request, 'bookmark/index.html', context)
    else:
        return render(request, "homepage.html")

@login_required
def inbox(request, username=None):
    inbox_list = get_object_or_404(List, kind=LIST_KIND_CHOICES.INBOX, user=request.user)
    return redirect('bookmark_user_list', username=username, id=inbox_list.id)

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
        elif filter == 'user':
            #users = User.objects.all()
            #context['users'] = users
            pass
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

def list_domain(request, domain):
    user = request.user
    context = {}
    bookmarks = Bookmark.objects.filter(domain=domain, list__public=True).order_by('-created_time')
    contributor_counts = bookmarks.values('user').annotate(count=Count('user', distinct=True))
    contributor_ids = []
    for contributor_count in contributor_counts:
        contributor_ids.append(contributor_count['user'])
    contributors = User.objects.filter(id__in=contributor_ids)
    context['contributors'] = contributors
    context['bookmarks'] = bookmarks
    context['domain'] = domain
    return render(request, 'bookmark/list_domain.html', context)

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
def sync(request):
    user = request.user
    if 'website' in request.GET:
        website = request.GET.get('website')
        request.session['redirect_to'] = reverse('bookmark_sync') + "?sync=" + website
        return redirect('socialauth_begin', website)
    github_synced = False
    if 'sync' in request.GET:
        website = request.GET.get('sync')
        if website == 'github':
            list_name = _('Github starred project')
            sync_github.delay(user, list_name)
            github_synced = True
            messages.info(request, _("Syncing is in progress, please wait for while.")) 

    else:
        try:
            state = SyncState.objects.get(user=user, website="github")
            github_synced = True
        except SyncState.DoesNotExist:
            github_synced = False
    context = {}
    context['github_synced'] = github_synced
    return render(request, 'bookmark/sync.html', context)

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

                if site == 'chrome':
                    list_name = _("Export from Chrome Browser ")
                elif site == 'kippt':
                    list_name = _('Export from Kippt')
                elif site == 'delicious':
                    list_name = _('Export from Delicious')
                elif site == 'google':
                    list_name = _('Export from Google Bookmarks')
                else:
                    return Http404()

                handle_imported_file.delay(data, user, site, list_name)
                messages.info(request, 
                              _("Upload successfully, \
                                we will import your bookmarks to your account \
                                in background.Please wait a minute."))
        return redirect('bookmark_import')

@login_required
def export(request):
    if request.method == 'POST':
        user = request.user

        lists = user.list_set.all()

        html = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <!--This is an automatically generated file.
        It will be read and overwritten.
        Do Not Edit! -->
        <Title>lianpeng.me bookmarks</Title>
        <H1>Bookmarks</H1>
        <DL>
        """

        for l in lists:
            bookmarks = l.bookmark_set.all()
            html += ''.join(['<DT><A HREF="{}" ADD_DATE="{}" TAGS="{}" LIST="{}">{}</A></DT>\n'.format(
                bookmark.url, calendar.timegm(bookmark.created_time.utctimetuple()), bookmark.tags, l.name, bookmark.title
            ) for bookmark in bookmarks])
        html += "</DL>"
        resp = HttpResponse(html, content_type="application/octet-stream")
        resp['Content-Disposition'] = 'attachment;filename=\"{}\"'.format('lianpeng_bookmarks.html') 
        return resp

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

@login_required
def bookmark_viewed(request, id):
    bookmark = get_object_or_404(Bookmark, id=id)
    user = request.user
    bookmark.save()
    return HttpResponse("opened")

