from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('note.views',
    url(r'^$', "index", name='note_index'),
    url(r'^(?P<id>\d+)/$', "detail", name='note_detail'),
    url(r'^edit/(?P<id>\d+)/$', "edit", name='note_edit'),
)
