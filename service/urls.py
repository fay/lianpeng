from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('service.views',
    url(r'^feed_url/$', "feed_url", name='service_feed_url'),
)
