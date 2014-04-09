"""Command for sending the newsletter"""
from django.core.management.base import NoArgsCommand
from django.utils import timezone

from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.models import Newsletter


class MailMan(Mailer):
    @property
    def can_send(self):
        """Check if the newsletter can be sent"""
        if self.newsletter.server.credits() <= 0:
            return False

        if self.test:
            return True

        if self.newsletter.sending_date <= timezone.now() and \
               (self.newsletter.status == Newsletter.WAITING or \
                self.newsletter.status == Newsletter.SENDING):
            return True

        return False

    def build_email_content(self, contact):
        """Generate the mail for a contact"""
        uidb36, token = tokenize(contact)
        context = Context({'contact': contact,
                           'domain': Site.objects.get_current().domain,
                           'newsletter': self.newsletter,
                           'uidb36': uidb36, 'token': token})

        content = self.newsletter_template.render(context)
        html_body = render_to_string("misc/email_templates/default.html", {'subject': newsletter.subject, 'body': content})
        return smart_unicode(content)


class Command(NoArgsCommand):
    """Send the newsletter in queue"""
    help = 'Send the newsletter in queue'

    def handle_noargs(self, **options):
        verbose = int(options['verbosity'])

        if verbose:
            print 'Starting sending newsletters...'

        for newsletter in Newsletter.objects.exclude(
            status=Newsletter.DRAFT).exclude(status=Newsletter.SENT):
            mailer = MailMan(newsletter)
            if mailer.can_send:
                if verbose:
                    print 'Start emailing %s' % newsletter.title
                mailer.run()

        if verbose:
            print 'End session sending'
