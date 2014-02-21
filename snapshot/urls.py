from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('snapshot.views',
    url(r'^$', "index", name='snapshot_index'),
)
