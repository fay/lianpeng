from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('market.views',
    url(r'^$', "index", name='market_index'),
    url(r'^alipay/notify/$', "alipay_notify", name='market_alipay_notify'),
    url(r'^order/$', "order", name='market_order'),
    url(r'^(?P<app_key>\w+)/$', "detail", name='market_app'),
)
