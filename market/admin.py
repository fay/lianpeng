from django.contrib import admin

from market.models import App, AppAction, UserApp

admin.site.register(App)
admin.site.register(UserApp)
admin.site.register(AppAction)
