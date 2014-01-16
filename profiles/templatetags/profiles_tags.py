from django.template.defaultfilters import register
from django.conf import settings
from django.contrib.auth.models import User

from gravatar.templatetags.gravatar import gravatar_for_email
from sorl.thumbnail import get_thumbnail

@register.simple_tag
def avatar(email, size):
    avatar_url = ""
    if email:
        user = User.objects.get(email=email)
        profile = user.get_profile()
        if profile.avatar:
            im = get_thumbnail(profile.avatar, '{}x{}'.format(size, size),
                    crop='center', quality=99)
            avatar_url = im.url + "?"
        else:
            avatar_url = gravatar_for_email(email, size)
    return avatar_url
