from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns("",
    url(r"^bind/", "misc.auth_pipeline.bind", name="bind_user"),
    url(r"^invite/", "misc.views.invite", name="invite_user"),
    url(r"^redirect_to_login/", "misc.auth_pipeline.redirect_to_login", name="redirect_to_login"),
    url(r"^resend/confirmation/$", "misc.views.resend_email_confirmation", name="resend_email_confirmation"),
    url(r"^resend/confirmation/done/$", "misc.views.resend_email_confirmation_done", name="resend_email_confirmation_done"),
)
