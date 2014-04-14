from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


from djcelery_email.backends import CeleryEmailBackend


class CeleryEmailWrapperBackend(CeleryEmailBackend):

    def send_messages(self, email_messages):
        html_msgs = []
        for msg in email_messages:
            html_msg = EmailMultiAlternatives(msg.subject, msg.body, msg.from_email, msg.to)
            html_body = render_to_string("misc/email_templates/default.html", {'subject': msg.subject, 'body': msg.body})
            html_msg.attach_alternative(html_body, "text/html")
            html_msgs.append(html_msg)

        return super(CeleryEmailWrapperBackend, self).send_messages(html_msgs)
