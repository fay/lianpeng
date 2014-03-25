from django.contrib import admin

from profiles.models import Profile

class ProfileAdmin(admin.ModelAdmin):

    def make_mailing_list(self, request, queryset):
        from emencia.django.newsletter.models import Contact
        from emencia.django.newsletter.models import MailingList

        subscribers = []
        for profile in queryset:
            if not profile.user.email:
                continue
            contact, created = Contact.objects.get_or_create(email=profile.user.email,
                                                             defaults={'first_name': profile.user.first_name,
                                                                       'last_name': profile.user.last_name,
                                                                       'content_object': profile})
            subscribers.append(contact)
        new_mailing = MailingList(name='New mailing list',
                                  description='New mailing list created from admin/profile')
        new_mailing.save()
        new_mailing.subscribers.add(*subscribers)
        new_mailing.save()
        self.message_user(request, '%s succesfully created.' % new_mailing)
    make_mailing_list.short_description = 'Create a mailing list'

    actions = ['make_mailing_list']
admin.site.register(Profile, ProfileAdmin)
