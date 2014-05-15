from django.contrib import admin
from bookmark.models import Bookmark, List, Feedback, PickedList
from account.models import EmailAddress
from screenshot.models import Screenshot

class ScreenshotInline(admin.StackedInline):
    model = Screenshot
    extra = 1

class BookmarkAdmin(admin.ModelAdmin):
    inlines = [ScreenshotInline]

admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(List)
admin.site.register(PickedList)
admin.site.register(Feedback)
admin.site.register(EmailAddress)
