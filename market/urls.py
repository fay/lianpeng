from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('market.views',
    url(r'^$', "index", name='market_index'),
    url(r'^order/(?P<app_key>\w+)/$', "order", name='market_order'),
)
