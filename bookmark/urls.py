from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('bookmark.views',
    url(r'^$', "index", name='bookmark_index'),
    url(r'^$', "index", name='home'),
    url(r'^explore/$', "explore", name='bookmark_explore'),
    url(r'^feedback/$', "feedback", name='bookmark_feedback'),
    url(r'^import/$', "import_to", name='bookmark_import'),
    url(r'^export/$', "export", name='bookmark_export'),
    url(r'^sync/$', "sync", name='bookmark_sync'),
    url(r'^list/(?P<id>\d+)/$', "list_detail", name='bookmark_list'),
    url(r'^list/domain/(?P<domain>[\w\-:.]+)/$', "list_domain", name='bookmark_list_domain'),
    url(r'^list/accept/(?P<id>\d+)/$', "list_accept_invitation", name='bookmark_list_accept'),
    url(r'^list/ignore/(?P<id>\d+)/$', "list_ignore_invitation", name='bookmark_list_ignore'),
    url(r'^bookmark/(?P<id>\d+)/$', "bookmark_detail", name='bookmark_detail'),
    url(r'^bookmark/viewed/(?P<id>\d+)/$', "bookmark_viewed", name='bookmark_viewed'),
    url(r'^tools/$', direct_to_template, {"template": "bookmark/tools.html"}, name="bookmark_tools"),

    url(r'^(?P<username>[\w]+)/$', "public_profile", name="bookmark_profile"),
    url(r'^(?P<username>[\w]+)/list/all$', "index"),
    url(r'^(?P<username>[\w]+)/list/feed$', "index"),
    url(r'^(?P<username>[\w]+)/list/recent$', "index"),
    url(r'^(?P<username>[\w]+)/search/(?P<query>.+)$', "index", name="bookmark_search"),
    url(r'^(?P<username>[\w]+)/tag/(?P<tag>.+)$', "index", name="bookmark_tag"),
    url(r'^(?P<username>[\w]+)/list/(?P<id>\d+)$', "index", name="bookmark_user_list"),
    url(r'^(?P<username>[\w]+)/inbox/$', "inbox"),
)
