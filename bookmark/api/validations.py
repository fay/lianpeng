from tastypie.validation import Validation, FormValidation
from bookmark.forms import BookmarkForm

class BookmarkValidation(FormValidation):
    def is_valid(self, bundle, request=None):
        l = bundle.obj.list
        errors = {}
        if l and (l.user != bundle.obj.user and \
                  not bundle.obj.user.has_perm('can_edit', l)):
            errors['user'] = 'Forbidden'
            return errors
        return super(BookmarkValidation, self).is_valid(bundle, request)

class ListInvitationValidation(FormValidation):

    def is_valid(self, bundle, request=None):
        l = bundle.obj.list
        errors = {}
        if l and l.user != bundle.request.user:
            errors['user'] = 'Forbidden'
            return errors
        return super(ListInvitationValidation, self).is_valid(bundle, request)

    
