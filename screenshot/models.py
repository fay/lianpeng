from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.db.models import F
from django.dispatch import receiver
from django.conf import settings

from bookmark.models import Bookmark

def screenhot_upload_to(instance, filename):
    bookmark = instance.bookmark
    user_dir = md5(bookmark.user.username + settings.SCREENSHOT_SALT).hexdigest()
    return os.path.join('screenshots', user_dir, filename)

class Screenshot(models.Model):
    bookmark = models.OneToOneField(Bookmark)
    image = models.ImageField(upload_to=screenhot_upload_to)
    created_time = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Bookmark)
def create_screenshot(sender, instance, created, **kwargs):
    try:
        instance.screenshot
    except Screenshot.DoesNotExist:
        no_screenshot = True
    else:
        no_screenshot = False
    if created or no_screenshot:
        from screenshot.tasks import create_screenshot_task
        user = instance.user
        create_screenshot_task.delay(instance)

@receiver(post_delete, sender=Screenshot)
def delete_screenshot_file(sender, instance, **kwargs):
    instance.image.delete(save=False)

