from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('harvest.views',
    url(r'^pageinfo/$', "index", name='harvest_index'),
    url(r'^bookmarklet.js$', "bookmarklet_js"),
    url(r'^bookmarklet.html$', "bookmarklet_popup", name="bookmarklet_popup"),
    url(r'^save$', "save_bookmark", name="save_bookmark"),
    url(r'^tag/$', "extract_tag", name="extract_tag"),
)
