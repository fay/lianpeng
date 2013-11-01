from django.template.defaultfilters import register
from django.conf import settings

from bookmark.models import Follow

@register.filter(name="is_user_followed")
def is_user_followed(user, followee):
    if user.is_authenticated():
        try:
            return user.following.get(followee=followee)
        except Follow.DoesNotExist:
            pass
    return False

@register.filter(name="list_bookmarks")
def list_bookmarks(l, num=3):
    return l.bookmark_set.order_by('-created_time')[:num]

@register.filter(name="public_lists")
def public_lists(user, num=3):
    return user.list_set.filter(public=True).order_by('-created_time')[:num]

@register.filter(name="split")
def split_string(string):
    if string:
        return string.split()
    else:
        return string
