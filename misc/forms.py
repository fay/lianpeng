from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from account.forms import SignupForm, LoginUsernameForm

class SocialSignupForm(SignupForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        widget=forms.TextInput(attrs={'class':'input-xlarge'}),
        required=True
    )
    password = forms.CharField(
        label=_("Password"), required=False,
        widget=forms.HiddenInput()
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"), required=False,
        widget=forms.HiddenInput()
    )
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-xlarge'}), required=True)

class LoginEmailOrUsernameForm(LoginUsernameForm):
    
    def user_credentials(self):
        identifier = self.cleaned_data[self.identifier_field]
        key = 'username'
        if '@' in identifier:
            try:
                identifier = User.objects.get(email=identifier).username
            except User.DoesNotExist:
                pass
        return {
            key: identifier,
            "password": self.cleaned_data["password"],
        }

