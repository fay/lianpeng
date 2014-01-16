from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import F
from django.utils.translation import ugettext as _

# Create your models here.
from idios.models import ProfileBase
from sorl.thumbnail import delete

class Profile(ProfileBase):
    avatar = models.ImageField(upload_to='avatars', verbose_name=_("Avatar"))
    location = models.CharField(max_length=64, null=True, blank=True, verbose_name=_("Location"))
    website = models.URLField(null=True, blank=True, verbose_name=_("Website"))
    signature = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("Signature"))
    about = models.TextField(max_length=256, null=True, blank=True, verbose_name=_("about"))

    douban = models.CharField(max_length=56, verbose_name=_("Douban"), null=True, blank=True)
    weibo = models.CharField(max_length=56, verbose_name=_("Weibo"), null=True, blank=True)
    twitter = models.CharField(max_length=56, verbose_name=_("Twitter"), null=True, blank=True)
    github = models.CharField(max_length=56, verbose_name=_("Github"), null=True, blank=True)
    dribbble = models.CharField(max_length=56, verbose_name=_("Dribbble"), null=True, blank=True)

@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.avatar:
        if not str(instance.avatar).startswith('avatars'):
            user = instance.user
            profile = user.get_profile()
            if profile.avatar:
                delete(profile.avatar)
