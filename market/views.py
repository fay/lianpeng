import urllib

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

from market.models import App, UserApp, AppPlan, Order, ORDER_STATES
from pprint import pprint
from alipay import alipay

def index(request):
    context = {}
    return render(request, 'market/index.html', context)

@login_required
def detail(request, app_key):
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



def alipay_notify(request):
    print '>>notify url handler start...'
    if request.method == 'POST':
        if alipay.notify_verify(request.POST):
            pprint('pass verification...')
            tn = request.POST.get('out_trade_no')
            pprint('Change the status of bill %s'%tn)
            order = Order.objects.get(pk=tn)
            trade_status = request.POST.get('trade_status')
            pprint('the status of bill %s changed to %s'% (tn,trade_status))
            order.trade_status = trade_status
            order.save()

            trade_no = request.POST.get('trade_no')
            if trade_status == 'WAIT_SELLER_SEND_GOODS':
                pprint('It is WAIT_SELLER_SEND_GOODS, so upgrade bill')
                order.finish()
                url = alipay.send_goods_confirm_by_platform(trade_no)
                pprint('send goods confirmation. %s'%url)
                req = urllib.urlopen(url)
                return HttpResponse("success")
        else:
            pprint ('##info: Status of %s' % trade_status)
            return HttpResponse ("success")
    return HttpResponse ("fail")

def order(request):
    context = {}
    orders = Order.objects.all()
    context['orders'] = orders
    return render(request, 'market/order.html', context)
