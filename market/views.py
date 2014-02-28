from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _

from market.models import App, UserApp, AppPlan, Order

from alipay import alipay

def index(request):
    context = {}
    return render(request, 'market/index.html', context)

@login_required
def order(request, app_key):
    user = request.user
    app = get_object_or_404(App, key=app_key)
    if request.method == 'GET':
        try:
            user_app = UserApp.objects.get(user=user, app__key=app_key)
        except UserApp.DoesNotExist:
            plans = AppPlan.objects.filter(app=app, available=True)
            context = {}
            context['app'] = app
            context['plans'] = plans

            return render(request, 'market/{}.html'.format(app_key), context)
            #return redirect('market_app', app_key=app_key)
        else:
            pass
    else:
        try:
            user_app = UserApp.objects.get(user=user, app__key=app_key)
        except UserApp.DoesNotExist:
            plan_id = request.POST.get('plan')
            amount = int(request.POST.get('amount'))
            plan = AppPlan.objects.get(id=int(plan_id))
            price = plan.price
            total = amount * price
            days = plan.period * amount

            order = Order(price=price, amount=amount, period=plan.period, user=user, app=app, plan=plan)
            order.save()
            payurl = alipay.trade_create_by_buyer(order.id, _("Pay for snapshot"), _('Pay for snapshot service of %(days)s days #%(order)s.') % ({'days': days, 'order': order.id}), total)
            return redirect(payurl)
