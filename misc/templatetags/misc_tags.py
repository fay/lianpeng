from django.template.defaultfilters import register
from django.conf import settings
from django.core.cache import cache
from bookmark.models import Bookmark

def grouped(l, n): 
    # Yield successive n-sized chunks from l.
    for i in xrange(0, len(l), n): 
        yield l[i:i+n]

@register.filter
def group_by(value, arg):
    return grouped(value, arg)

@register.simple_tag()
def total_bookmarks():
    total = cache.get('lp_total_bookmarks')
    if not total:
        total = Bookmark.objects.all().count()
        cache.set('lp_total_bookmarks', total, 60 * 60 * 1)
    return total

