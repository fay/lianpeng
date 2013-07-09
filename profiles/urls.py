from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('profiles.views',
    url(r'^$', "index", name='profiles_index'),
)
