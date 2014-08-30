from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('service.views',
    url(r'^feed_url/$', "feed_url", name='service_feed_url'),
    url(r'^favicon/$', "favicon", name='service_favicon'),
    url(r'^html2pdf/$', "html2pdf", name='service_html2pdf'),
)
