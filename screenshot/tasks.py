import os
from subprocess import Popen, PIPE
from celery.task import task

from django.conf import settings

from screenshot.models import Screenshot

@task
def create_screenshot_task(bookmark):
    url = bookmark.url
    image = "{}/screenshots/{}.png".format(settings.MEDIA_ROOT, bookmark.unique_key)
    image_url = "screenshots/{}.png".format(bookmark.unique_key)
    args = "wkhtmltoimage --disable-javascript --height 786 --quality 80 {} {}".format(url, image).split()
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print stdout, stderr
    if os.path.isfile(image):
        screenshot = Screenshot(bookmark=bookmark)
        screenshot.image.name = image_url
        screenshot.save()

def screenshot_by_phantomjs():
    driver = webdriver.PhantomJS() # or add to your PATH
    driver.set_window_size(1024, 796) # optional
    driver.set_page_load_timeout(20) 
    driver.get(url)
    driver.save_screenshot(target) # save a screenshot to disk
    driver.quit()
