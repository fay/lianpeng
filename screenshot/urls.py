from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('screenshot.views',
    url(r'^$', "index", name='screenshot_index'),
)
