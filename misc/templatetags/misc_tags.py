from django.template.defaultfilters import register
from django.conf import settings

def grouped(l, n): 
    # Yield successive n-sized chunks from l.
    for i in xrange(0, len(l), n): 
        yield l[i:i+n]

@register.filter
def group_by(value, arg):
    return grouped(value, arg)

