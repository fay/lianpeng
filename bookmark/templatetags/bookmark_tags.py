from django.template.defaultfilters import register
from django.conf import settings

@register.filter
def following_users(user):
    return user.following.filter(target_user__id__gt=0)

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
