import time
import random

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from account.views import SignupView
from account.forms import SignupForm
from misc.forms import SocialSignupForm
from social_auth.utils import setting, dsa_urlopen


def redirect_to_bind_form(*args, **kwargs):
    if not kwargs['request'].session.get('pass_bind') and \
       kwargs.get('user') is None:
        return redirect('bind_user')
    else:
        user = kwargs['request'].user
        if user.is_authenticated():
            return {"user": kwargs['request'].user}

def bind(request):
    name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
    try:
        backend = request.session[name]['backend']
    except:
        return redirect("account_login")
    c = {}
    if request.method == 'GET':
        form = SocialSignupForm()
    else:
        timestamp = int(time.time() * 1000)
        password = random.randrange(timestamp - 100000, timestamp)
        form = SocialSignupForm(request.POST)
        if form.is_valid():
            signup_view = SignupView()
            signup_view.request = request
            form.cleaned_data['password'] = password
            form.cleaned_data['password_confirm'] = password
            signup_view.form_valid(form)
            request.session['pass_bind'] = True
            return redirect('socialauth_complete', backend=backend)
    c['form'] = form
    c['backend'] = backend
    return render(request, 'misc/bind.html', c)

def redirect_to_login(request):
    redirect_url = request.GET.get('next')
    request.session['redirect_to'] = redirect_url
    return redirect('account_login')

def follow(*args, **kwargs):
    if not kwargs['request'].session.get('followed') and kwargs['request'].session.get('pass_bind'):
        return redirect('bind_follow')

