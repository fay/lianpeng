from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from account.models import EmailAddress

@login_required
def invite(request):
    c = {}
    return render(request, 'misc/invite.html', c)

@login_required
def resend_email_confirmation_done(request):
    context = {}
    context['email'] = request.user.email
    context['success_url'] = '/'
    return render(request, 'account/email_confirmation_sent.html', context)

@login_required
def resend_email_confirmation(request):
    user = request.user
    email_addr, created = EmailAddress.objects.get_or_create(email=user.email, defaults={"user": user})
    if created:
        if email_addr.verified:
            return redirect('/')
    confirmation = email_addr.send_confirmation()
    return redirect('resend_email_confirmation_done')


