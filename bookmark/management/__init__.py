from django.utils.translation import ugettext_noop as _
from django.db.models import signals
from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.NoticeType.create("new_comment", _("New comment"), _("You have a new comment"))
        notification.NoticeType.create("new_follower", _("New follower"), _("You have a new follower"))

    signals.post_syncdb.connect(create_notice_types, sender=notification)
