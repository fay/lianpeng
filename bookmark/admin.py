from django.contrib import admin
from bookmark.models import Bookmark, List, Feedback, PickedList
from account.models import EmailAddress
admin.site.register(Bookmark)
admin.site.register(List)
admin.site.register(PickedList)
admin.site.register(Feedback)
admin.site.register(EmailAddress)
