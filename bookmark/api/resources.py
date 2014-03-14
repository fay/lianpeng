from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication, BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.validation import Validation, FormValidation
from tastypie import fields
from tastypie.exceptions import TastypieError, Unauthorized
from tastypie.utils import trailing_slash
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, \
        HydrationError, InvalidSortError, ImmediateHttpResponse, Unauthorized

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, \
        MultipleObjectsReturned, ValidationError
from django.conf.urls import patterns, include, url
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.contrib.comments.models import Comment  
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.humanize.templatetags import humanize

from profiles.templatetags.profiles_tags import avatar
from fluent_comments.templatetags.fluent_comments_tags import comments_count

from guardian.shortcuts import get_perms
from guardian.shortcuts import get_objects_for_user
from haystack.query import SearchQuerySet

from bookmark.models import Bookmark, List, Feedback, Follow, FollowList, \
        ListInvitation, FeedCount
from bookmark.api.validations import BookmarkValidation, \
        ListInvitationValidation
from bookmark.forms import BookmarkForm, ListForm, FeedbackForm, FollowForm, \
        CommentForm, ListInvitationForm
from market.models import UserApp, App
from tagging.managers import ModelTaggedItemManager
from misc.models import UserTour
from snapshot.models import Snapshot

class PermissionValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Not quite what I had in mind.'}

        errors = {}

        if bundle.obj:
            if bundle.obj.user != request.user:
                errors['user'] = 'Forbidden'
        return errors

class PermissionAuthorization(DjangoAuthorization):

    def read_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).read_list(
            object_list, bundle)
        if result:
            user = bundle.request.user
            result = result.filter(user=user)
        return result

    def read_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        if bundle.request.user != bundle.obj.user:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def create_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).create_list(
            object_list, bundle)
        if result:
            if bundle.request.user != bundle.obj.user:
                result = []
        return result

    def create_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        bundle.obj.user = bundle.request.user
        return True 

    def update_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).update_list(
            object_list, bundle)
        if result:
            if bundle.request.user != bundle.obj.user:
                result = []
        return result 

    def update_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        if bundle.request.user != bundle.obj.user:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def delete_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).delete_list(
            object_list, bundle)
        if result:
            if bundle.request.user != bundle.obj.user:
                result = []
        return result 

    def delete_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)

        if klass is False:
            return []
        if bundle.request.user != bundle.obj.user:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

class BookmarkAuthorization(PermissionAuthorization):

    def read_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        user = bundle.request.user
        if bundle.obj.list.public or \
           user == bundle.obj.user or \
           user.has_perm('can_view', bundle.obj.list) or \
           user.has_perm('can_edit', bundle.obj.list):
            return True
        else:
            raise Unauthorized("You are not allowed to access that resource.")

    def update_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        user = bundle.request.user
        if user == bundle.obj.user or \
           user.has_perm('can_edit', bundle.obj.list):
            return True
        else:
            raise Unauthorized("You are not allowed to access that resource.")

    def delete_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)

        if klass is False:
            return []
        user = bundle.request.user
        if user == bundle.obj.user or \
           user.has_perm('can_edit', bundle.obj.list) or \
           user == bundle.obj.list.user:
            return True
        else:
            raise Unauthorized("You are not allowed to access that resource.")

class ListAuthorization(PermissionAuthorization):

    def read_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).read_list(
            object_list, bundle)
        if result:
            user = bundle.request.user
            can_edits = get_objects_for_user(bundle.request.user, 'bookmark.can_edit')
            if 'only_edit' in bundle.request.GET:
                result = result.filter(user=user) | can_edits
            else:
                can_views = get_objects_for_user(bundle.request.user, 'bookmark.can_view')
                result = result.filter(user=user) | can_views | can_edits
        return result

    def read_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        user = bundle.request.user
        if user == bundle.obj.user or \
           user.has_perm('can_view', bundle.obj) or \
           user.has_perm('can_edit', bundle.obj):
            return True
        else:
            raise Unauthorized("You are not allowed to access that resource.")

class ListInvitationAuthorization(PermissionAuthorization):

    def create_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            return []
        bundle.obj.user = bundle.request.user
        if bundle.obj.list.user == bundle.request.user:
            return True
        else:
            raise Unauthorized("You are not allowed to access that resource.")


class CommentAuthorization(PermissionAuthorization):

    def read_list(self, object_list, bundle):
        result = super(PermissionAuthorization, self).read_list(
            object_list, bundle)
        return result

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['get',]
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()

class ListResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user')
    kind = fields.IntegerField(readonly=True, attribute="kind")
    #bookmarks = fields.ToManyField('bookmark.api.resources.BookmarkResource', 'bookmarks')

    class Meta:
        model = List
        queryset = List.objects.order_by("kind", "-modified_time", "position")
        fields = ['name', 'public', 'position', 'id', 'kind', 'count']

        allowed_methods = ['get', 'put', 'post', 'delete']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = ListAuthorization()
        validation = FormValidation(form_class=ListForm)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/bookmarks%s$" % 
                (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('get_bookmarks'), 
                name="api_get_list_bookmarks"),
        ]

    def get_shared_lists(self, request, **kwargs):
        return self.get_list(request, only_share=True)

    def obj_get_list(self, bundle, **kwargs):
        if 'only_share' in kwargs:
            objects = get_objects_for_user(bundle.request.user, ['bookmark.can_view', 'bookmark.can_edit']).exclude(user=bundle.request.user)
        else:
            objects = super(ListResource, self).obj_get_list(bundle, **kwargs)
        return objects

    def dehydrate(self, bundle):
        user = bundle.request.user
        bundle.data['perms'] = get_perms(user, bundle.obj)
        try:
            avatar = avatar(bundle.obj.user.email, 14)
        except Exception:
            avatar = ""
        bundle.data['user_avatar'] = avatar
        bundle.data['user_name'] = bundle.obj.user.username
        if bundle.obj.user != bundle.request.user:
            bundle.data['kind'] = 3 
        return bundle

    def get_bookmarks(self, request, **kwargs):
        child_resource = BookmarkResource()
        return child_resource.get_list(request, list_id=kwargs.get('pk'))

    def obj_delete(self, bundle, **kwargs):
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the \
                               provided arguments could not be found.")
        user = bundle.request.user
        if bundle.obj.user != user:
            try:
                li = ListInvitation.objects.get(invitee=user.username, user=bundle.obj.user, list=bundle.obj)
                li.delete()
            except ListInvitation.DoesNotExist:
                pass
        else:
            if bundle.obj.kind == 2:
                super(ListResource, self).obj_delete(bundle, **kwargs)

class BookmarkResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user', readonly=True)
    list = fields.ForeignKey(ListResource, 'list', null=True)
    domain = fields.CharField('domain', readonly=True)

    class Meta:
        model = Bookmark
        queryset = Bookmark.objects.order_by('-created_time')
        fields = ['id', 'title', 'domain', 'tags', 'url', 'note', 'user', 'list', 'created_time', 'unique_key', 'charset']
        allowed_methods = ['get', 'put', 'post', 'delete']
        always_return_data = True #: when new object is created return the data with all fields
        authentication = SessionAuthentication()
        authorization = BookmarkAuthorization()
        #validation = PermissionValidation()
        validation = BookmarkValidation(form_class=BookmarkForm)
        filtering = {
            'url': ['exact'],
            'tag':['exact'],
            'feed':ALL
        }

    def dehydrate(self, bundle):
        user = bundle.obj.user
        bundle.data['user_avatar'] = avatar(user.email, 64)
        bundle.data['user_name'] = user.username
        bundle.data['timesince'] = humanize.naturaltime(bundle.data['created_time'])
        bundle.data['comments_count'] = comments_count(bundle.obj)
        bundle.data['favicon'] = bundle.obj.favicon
        bundle.data['list_name'] = bundle.obj.list.name
        bundle.data['list_id'] = bundle.obj.list.id

        #: snapshot
        has_snapshot = False
        try:
            bundle.obj.snapshot
        except Snapshot.DoesNotExist:
            pass
        else:
            has_snapshot = True
        bundle.data['has_snapshot'] = has_snapshot

        return bundle

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def obj_get_list(self, bundle, **kwargs):

        user = bundle.request.user

        # by list
        list_id = kwargs.get('list_id')
        objects = super(BookmarkResource, self).obj_get_list(bundle, **kwargs)
        if list_id:
            l = List.objects.get(id=list_id)
            if user.has_perm('can_view', l) or user.has_perm('can_edit', l) or l.user == user:
                objects = Bookmark.objects.all()
            objects = objects.filter(list=l).order_by('-created_time')

        # by recent
        recent = bundle.request.GET.get('recent')
        if recent:
            objects = objects.order_by('-modified_time')
        # user feed
        feed = bundle.request.GET.get('feed')
        if feed:
            objects = Bookmark.objects.feed(user)

        # by tag
        tags = bundle.request.GET.get('tag')
        if tags:
            mtim = ModelTaggedItemManager()
            objects = mtim.with_all(tags, objects)

        q = bundle.request.GET.get('q')
        if q:
            try:
                UserApp.objects.get(user=user, app__key='search')
                sqs = SearchQuerySet().models(Bookmark).auto_query(q).filter(user_id=user.id)
                objects = objects.filter(pk__in=[i.pk for i in sqs])
            except UserApp.DoesNotExist:
                objects = objects.filter(Q(title__icontains=q) | Q(tags__icontains=q) | Q(note__icontains=q))

        return objects

class FeedbackResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user', null=True)

    class Meta:
        model = Feedback
        queryset = Feedback.objects.order_by('-created_time')
        fields = ['text']
        allowed_methods = ['post']
        authorization = PermissionAuthorization()
        validation = FormValidation(form_class=FeedbackForm)

class FollowResource(ModelResource):

    follower = fields.ForeignKey(UserResource, 'user')
    followee = fields.ForeignKey(UserResource, 'followee')

    class Meta:
        model = Follow
        queryset = Follow.objects.order_by('-created_time')
        allowed_methods = ['get', 'post', 'delete']
        always_return_data = True
        fields = ['follower', 'id', 'followee']
        authentication = SessionAuthentication()
        authorization = PermissionAuthorization()
        validation = FormValidation(form_class=FollowForm)

class FollowListResource(ModelResource):

    follower = fields.ForeignKey(UserResource, 'user')
    list = fields.ForeignKey(UserResource, 'user')

    class Meta:
        model = FollowList
        queryset = FollowList.objects.order_by('-created_time')
        allowed_methods = ['get', 'post', 'delete']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = PermissionAuthorization()

class CommentResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user')
    content_object = GenericForeignKeyField({
        Bookmark: BookmarkResource,
        #List: ListResource
    }, 'content_object')

    class Meta:
        model = Comment
        queryset = Comment.objects.all()
        allowed_methods = ['get', 'post', 'delete']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = CommentAuthorization()
        validation = FormValidation(form_class=CommentForm)
        filtering = {
            'object_pk': ALL
        }

    def dehydrate(self, bundle):
        user = bundle.obj.user
        bundle.data['avatar'] = avatar(user.email, 32)
        bundle.data['user_name'] = user.username
        bundle.data['submit_date'] = humanize.naturaltime(bundle.data['submit_date'])
        return bundle

class ListInvitationResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user', readonly=True)
    list = fields.ForeignKey(ListResource, 'list')

    class Meta:
        model = ListInvitation
        queryset = ListInvitation.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = PermissionAuthorization()
        validation = ListInvitationValidation(form_class=ListInvitationForm)
        filtering = {
            'list': ['exact'] 
        }

    def dehydrate(self, bundle):
        bundle.data['user_name'] = bundle.obj.invitee
        return bundle

class UserTourResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user', readonly=True)

    class Meta:
        model = UserTour
        queryset = UserTour.objects.all()
        allowed_methods = ['get', 'put']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = PermissionAuthorization()

class FeedCountResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user', readonly=True)

    class Meta:
        model = FeedCount
        queryset = FeedCount.objects.all()
        allowed_methods = ['get', 'put']
        always_return_data = True
        authentication = SessionAuthentication()
        authorization = PermissionAuthorization()
