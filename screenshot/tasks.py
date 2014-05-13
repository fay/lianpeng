import os
from celery.task import task

from django.conf import settings

from screenshot.models import Screenshot

@task
def create_screenshot_task(bookmark):
    url = bookmark.url
    image = "{}/screenshots/{}.png".format(settings.MEDIA_ROOT, bookmark.unique_key)
    image_url = "{}screenshots/{}.png".format(settings.MEDIA_URL, bookmark.unique_key)
    os.system("wkhtmltoimage --height 786 --quality 80 {} {}".format(url, image))
    screenshot = Screenshot(bookmark=bookmark)
    screenshot.image.name = image_url
    screenshot.save()

