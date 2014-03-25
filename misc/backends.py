from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.template.loader import render_to_string

from djcelery_email.backends import CeleryEmailBackend


class CeleryEmailWrapperBackend(CeleryEmailBackend):

    def send_messages(self, email_messages):
        for msg in email_messages:
            msg.body = render_to_string("misc/email_templates/default.html", {'body': msg.body})
        return super(CeleryEmailWrapperBackend, self).send_messages(email_messages)
