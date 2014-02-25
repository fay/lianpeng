import xadmin
from xadmin import views
from models import *
from xadmin.layout import *

from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction

from market.models import App, UserApp, AppPlan

xadmin.site.register(App)
xadmin.site.register(AppPlan)
xadmin.site.register(UserApp)

