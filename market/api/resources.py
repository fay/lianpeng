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

from market.models import App, AppAction, AppList

class AppResource(ModelResource):

    actions = fields.ToManyField('market.api.resources.AppActionResource', 'appaction_set', full=True)

    class Meta:
        queryset = App.objects.all()
        allowed_methods = ['get',]
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()

class AppActionResource(ModelResource):

    class Meta:
        queryset = AppAction.objects.all()
        allowed_methods = ['get',]
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()

class AppListResource(ModelResource):

    app = fields.ForeignKey(AppResource, 'app', full=True)

    class Meta:
        queryset = AppList.objects.all()
        allowed_methods = ['get',]
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
