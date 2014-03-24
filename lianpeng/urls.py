from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib import admin

from account.views import SignupView, LoginView, SettingsView
import xadmin
xadmin.autodiscover()
from xadmin.plugins import xversion
xversion.registe_models()

admin.autodiscover()

from bookmark.api.resources import BookmarkResource, \
         UserResource, ListResource, FeedbackResource, \
        FollowResource, FollowListResource, CommentResource, \
        ListInvitationResource, UserTourResource, FeedCountResource
from bookmark.forms import SignupForm, SettingsForm
from misc.forms import LoginEmailOrUsernameForm

from tastypie.api import Api
v1_api = Api(api_name='v1')
v1_api.register(BookmarkResource())
v1_api.register(ListResource())
v1_api.register(UserResource())
v1_api.register(FeedbackResource())
v1_api.register(FollowResource())
v1_api.register(CommentResource())
v1_api.register(FollowListResource())
v1_api.register(ListInvitationResource())
v1_api.register(UserTourResource())
v1_api.register(FeedCountResource())

urlpatterns = patterns("",
    #url(r"^admin/", include(admin.site.urls)),
    url(r'adminx/', include(xadmin.site.urls)),
    url(r'^harvest/', include("harvest.urls")),
    url(r"^accounts/signup/$", SignupView.as_view(form_class=SignupForm), name="account_signup"),
    url(r"^accounts/settings/$", SettingsView.as_view(form_class=SettingsForm), name="account_settings"),
    url(r"^accounts/login/$", LoginView.as_view(form_class=LoginEmailOrUsernameForm), name="account_login"),

    url(r'', include('social_auth.urls')),
    url(r'misc/', include('misc.urls')),
    url(r"^accounts/", include("account.urls")),
    url(r'^api/', include(v1_api.urls)),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^profiles/profile/(?P<username>\w+)/', redirect_to, {'url': '/profiles/edit'}),
    url(r'^help/', direct_to_template, {'template': 'help.html'}, name="help"),
    url(r'^about/', direct_to_template, {'template': 'about.html'}, name="about"),
    url(r'^profiles/', include('idios.urls')),
    url(r'^invite/', include('kaleo.urls')),
    url(r'^notifications/', include('notifications.urls', namespace="notifications")),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^snapshot/', include('snapshot.urls')),
    url(r'^app/', include('market.urls')),
    url(r'^500/$', direct_to_template, {'template': '500.html'}),
    url(r"^likes/", include("phileo.urls")),
    url(r'^', include("bookmark.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
