from hashlib import md5
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.db.models import F
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.contrib.comments.models import Comment  
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.timezone import utc
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


from tagging.fields import TagField
import positions
from notifications import notify
from notifications.models import Notification
from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from agon.models import award_points, TargetStat
from misc.utils import find_mentions

class DiffingMixin(object):

    def __init__(self, *args, **kwargs):
        super(DiffingMixin, self).__init__(*args, **kwargs)
        self._original_state = dict(self.__dict__)

    def get_changed_columns(self):
        missing = object()
        result = {}
        for key, value in self._original_state.iteritems():
            if key != self.__dict__.get(key, missing):
                result[key] = value
        return result

class List(models.Model):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User)
    image = models.ImageField(null=True, blank=True, 
                              upload_to="list_images")
    slug = models.SlugField(null=True, blank=True)
    public = models.BooleanField(default=False, db_index=True)
    kind = models.IntegerField(choices=((0, "inbox"), 
                                        (2, "normal"), 
                                        (3, "shared")), 
                               # Note: kind: 3(shared) is not used in db, 
                               # but for frontend use, kind: 1 is reserved
                               default=2, db_index=True) 
    position = positions.PositionField(unique_for_fields=('user', 'kind'))
    count = models.PositiveIntegerField(default=0)

    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)

    def __unicode__(self):
        return self.name

    def absolute_url(self):
        url = reverse('bookmark_list', args=(self.id, ))
        return url

    class Meta:
        permissions = (
            ('can_view', 'Can view'),
            ('can_edit', 'Can edit'),
        )

class ListUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(List)

class ListGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(List)

class Bookmark(models.Model, DiffingMixin):
    url = models.URLField()
    title = models.CharField(max_length=1024)
    domain = models.CharField(max_length=128, blank=True, null=True,
                              db_index=True)
    note = models.TextField(null=True, blank=True)
    tags = TagField()

    created_time = models.DateTimeField(db_index=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)
    unique_key = models.CharField(max_length=32)
    user = models.ForeignKey(User, related_name="bookmarks")
    list = models.ForeignKey(List, null=True, blank=True)

    def tags_splited(self):
        return self.tags.split(" ")

    def absolute_url(self):
        return reverse('bookmark_detail', args=[self.id])

    def __unicode__(self):
        return self.title

class Follow(models.Model):
    followee = models.ForeignKey(User, related_name='followers')
    user = models.ForeignKey(User, related_name='following')

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("followee", "user"), )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.followee == self.user:
            raise ValidationError(_("can not follow yourself"))

    def __unicode__(self):
        return "%s follows %s" % (self.user, self.followee)

class FollowList(models.Model):
    list = models.ForeignKey(List)
    user = models.ForeignKey(User)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("list", "user"), )

class PickedList(models.Model):
    list = models.OneToOneField(List, unique=True)
    user = models.ForeignKey(User)

class Feedback(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    text = models.TextField(verbose_name=_('feedback'))

    def __unicode__(self):
        return self.text

class ListInvitation(models.Model):
    invitee = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    list = models.ForeignKey(List)
    status = models.IntegerField(default=0, choices=((0, 'created'), 
                                                     (1, 'accepted'), 
                                                     (2, 'ignored')))
    permission = models.CharField(max_length=50, choices=(('can_edit', 'Can edit'), ('can_view', 'Can view')))
    created_time = models.DateTimeField(auto_now_add=True)

    def clean(self):

        if self.list.user != self.user or self.invitee == self.user.username:
            raise ValidationError(_("forbidden"))

    def actions(self):
        if self.status == 0:
            return [{'action_url': reverse('bookmark_list_accept', 
                                           args=(self.id, )),
                     'action_title': _("Accept"), 'action_level': 'success'
                    },
                    {'action_url': reverse('bookmark_list_ignore', 
                                           args=(self.id, )),
                     'action_title': _("Ignore"), 'action_level': ''
                    },
                   ]
        else:
            return []

    class Meta:
        unique_together = (('list', 'user', 'invitee'))


class SyncState(models.Model):
    user = models.ForeignKey(User)
    website = models.CharField(max_length=16)
    state = models.IntegerField(choices=((0, 'no sync'), (1, 'synced'), (2, 'syncing')))
    list = models.ForeignKey(List, null=True)

    class Meta:
        unique_together = (("user", "website"), )

@receiver(pre_delete, sender=ListInvitation)
def delete_permission(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.invitee)
    except User.DoesNotExist:
        pass
    else:
        invitation = instance
        perms = get_perms(user, invitation.list)
        for perm in perms:
            remove_perm(perm, user, invitation.list)
    

@receiver(post_save, sender=ListInvitation)
def update_permission(sender, instance, created, **kwargs):
    if not created:
        try:
            user = User.objects.get(username=instance.invitee)
        except User.DoesNotExist:
            pass
        else:
            invitation = instance
            perms = get_perms(user, invitation.list)
            for perm in perms:
                remove_perm(perm, user, invitation.list)
            assign_perm(invitation.permission, user, invitation.list)

@receiver(pre_save, sender=Bookmark)
def generate_unique_key(sender, instance, **kwargs):
    if not instance.unique_key:
        salt = "ASDHHWEAW2378232"
        key = md5("%s%s%s" % (instance.url.decode('utf-8'), 
                              instance.user.id, salt)).hexdigest()
        instance.unique_key = key
    if not instance.created_time:
        instance.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)

@receiver(post_save, sender=Bookmark)
def inc_list_count(sender, instance, created, **kwargs):
    l = instance.list
    if l and created:
        l.count = F('count') + 1
        l.save()

@receiver(post_save, sender=Bookmark)
def inc_user_karma(sender, instance, created, **kwargs):
    if created:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        today = now.date()
        user = instance.user
        today_count = Bookmark.objects.filter(created_time__gte=today, user=user).count()

        if today_count < 2:
            try:
                stat = user.targetstat_targets
                level = stat.level
            except TargetStat.DoesNotExist:
                level = 1
            award_points(user, 'daily_bookmark_' + str(level))
            total = Bookmark.objects.filter(user=user, id__gt=5000).count()
            stat = user.targetstat_targets
            next_level = level
            if 1000 > total >= 500:
                next_level = 2
            elif 5000 > total >= 1000:
                next_level = 3
            elif total >= 5000:
                next_level = 4
            if next_level != level:
                stat.level = next_level
                stat.save()

@receiver(pre_save, sender=Bookmark)
def update_list_count(sender, instance, **kwargs):
    if instance.id:
        old_list_id = instance.get_changed_columns().get('list_id')
        try:
            l = List.objects.get(id=old_list_id)
        except List.DoesNotExist:
            pass
        else:
            #: decrease old list count 
            if l and l.count > 0:
                l.count = F('count') - 1
                l.save()
            #: increase new list count
            l = instance.list
            l.count = F('count') + 1
            l.save()
        
@receiver(pre_delete, sender=Bookmark)
def dec_list_count(sender, instance, **kwargs):
    l = instance.list
    if l and l.count > 0:
        l.count = F('count') - 1
        l.save()

@receiver(post_save, sender=User)
def create_default_list(sender, instance, created, **kwargs):
    if created and instance.id > 0:
        default_list = List(user=instance, kind=0, name=_("Inbox"))
        default_list.save()

@receiver(pre_save, sender=Bookmark)
def append_to_inbox_list(sender, instance, **kwargs):
    if not instance.list:
        inbox = List.objects.get(user=instance.user, kind=0)
        instance.list = inbox

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        from django.utils.translation import ugettext_noop as _
        comment = instance
        user = comment.content_object.user
        from_user = comment.user
        mentions = set(find_mentions(comment.comment) + [from_user.username, user.username]) - set([from_user.username, user.username])
        users = list(User.objects.filter(username__in=mentions))
        users.append(user)
        for user in users:
            if user == from_user:
                continue
            notify.send(from_user, recipient=user, verb=_('replied'), 
                        action_object=comment,
                        description=comment.comment, 
                        target=comment.content_object)
        
@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    if created:
        from django.utils.translation import ugettext_noop as _
        user = instance.followee
        from_user = instance.user
        if user == from_user:
            return
        notify.send(from_user, recipient=user, verb=_('followed you'), 
                    action_object=instance)

@receiver(post_save, sender=ListInvitation)
def notify_invite(sender, instance, created, **kwargs):
    if created:
        from_user = instance.user
        try:
            recipient = User.objects.get(username=instance.invitee)
        except User.DoesNotExist:
            pass
        else:
            from django.utils.translation import ugettext_noop as _
            notify.send(from_user, recipient=recipient, 
                        verb=_('invited you to join'), 
                        action_object=instance, target=instance.list
                       )

@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    content = render_to_string('notifications/notice.txt', {'notice': instance})
    site = Site.objects.get_current()
    site_name = site.name 
    send_mail(_('[%(site_name)s] You have new notification messages') % {'site_name': site_name}, content,
              settings.DEFAULT_FROM_EMAIL, [instance.recipient.email], fail_silently=False)
    

'''
from django.contrib.auth.models import Group, Permission
def add_bookmark_permission(sender, instance, **kwargs):
    add_permission(instance, "bookmark")
    add_permission(instance, "list")

def add_permission(instance, suffix_code_name):
    add_permission = Permission.objects.get(codename="add_" + suffix_code_name)
    change_permission = Permission.objects.get(codename="change_" + suffix_code_name)
    delete_permission = Permission.objects.get(codename="delete_" + suffix_code_name)
    instance.user_permissions.add(add_permission)
    instance.user_permissions.add(delete_permission)
    instance.user_permissions.add(change_permission)
post_save.connect(add_bookmark_permission, sender=User)
'''
