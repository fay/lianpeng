from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

def invite(request):
    c = {}
    return render(request, 'misc/invite.html', c)
