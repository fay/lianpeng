from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns("",
    url(r"^bind/", "misc.auth_pipeline.bind", name="bind_user"),
    url(r"^redirect_to_login/", "misc.auth_pipeline.redirect_to_login", name="redirect_to_login"),
)
