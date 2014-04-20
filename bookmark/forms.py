#coding: utf-8
from urlparse import urlparse

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import resolve, Resolver404
from django.forms import ValidationError
from django.contrib.comments.models import Comment

from account.forms import SignupForm as OriginSignupForm, SettingsForm as OriginSettingsForm
from account.conf import settings
from account.models import EmailAddress
from notifications import notify

from bookmark.models import Bookmark, List, Feedback, Follow, FollowList, \
        ListInvitation

RESERVED_USERNAMES = "about access account accounts add address adm admin administration adult " \
                     "advertise ad ads advertising affiliate affiliates ajax analytics android anon anonymous api app apps archive atom " \
                     "auth authentication avatar backup banner banners bin billing blog blogs board bot bots business " \
                     "chat cache cadastro calendar campaign careers cgi client cliente code comercial " \
                     "compare config connect contact contest create code compras css " \
                     "dashboard data db design delete demo design designer dev devel dir " \
                     "directory doc docs domain download downloads " + "edit editor email ecommerce "\
                     "forum forums faq favorite feed feedback flog follow file files free ftp "\
                     "gadget gadgets games guest group groups " + "help home homepage host hosting hostname html http httpd https hpg "\
                     "info information image img images imap index invite intranet indice " + "java javascript job jobs js " + "knowledgebase " \
                     "ipad iphone irc " + "log login logs logout list lists " + "mail mail1 mail2 mail3 mail4 mail5 mailer mailing mx manager marketing " \
                     "master me media message microblog microblogs mine mp3 msg msn mysql " \
                     "messenger mob mobile movie movies music musicas my " + "name named net network new news newsletter nick nickname notes noticias " \
                     "ns ns1 ns2 ns3 ns4 " +  "old online operator order orders " + "page pager pages panel password perl pic pics photo photos photoalbum "\
                     "php plugin plugins pop pop3 post postmaster " + "postfix posts profile project projects promo pub public python " \
                     "random register registration root ruby rss " + "sale sales sample samples script scripts secure send service shop "\
                     "sql signup signin search security settings setting setup site " + "sites sitemap smtp soporte ssh stage staging start subscribe " \
                     "subdomain suporte support stat static stats status store streader read ores system " \
                     "tablet tablets tech telnet test test1 test2 test3 teste tests theme " + "themes tmp todo task tasks tools tv talk "\
                     "update upload url user username usuario usage " + "vendas video videos visitor " \
                     "win ww www www1 www2 www3 www4 www5 www6 www7 wwww wws wwws web webmail " + "website websites webmaster workshop " \
                     "xxx xpg " + "you yourname yourusername yoursite yourdomain " \
                     "weibo django site_media bookmark bookmarks shuqian share harvest " \
                     "love comment comments room tea explore discover reader read import tag tags sync"\

class ImportForm(forms.Form):
    site = forms.ChoiceField(choices=(("delicious", "Delicious"), ('google', "Google Bookmarks"), ("chrome", _("Chrome Browser Bookmarks")), ("kippt", "Kippt")), label=_("Choose Site you want to import from"))
    file = forms.FileField(max_length=1024, label=_("Upload File"))

class SignupForm(OriginSignupForm):
    username = forms.CharField(
        label=_("Username"),
        min_length=3,
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )

    def clean_username(self):
        username = super(SignupForm, self).clean_username()
        if username not in RESERVED_USERNAMES.split(" "):
            return username
        raise ValidationError(_(u'This username is a reserved username, please choose another one.'))

class SettingsForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True)

    def clean_email(self):
        value = self.cleaned_data["email"]
        if self.initial.get("email") == value:
            return value
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))
    

class BookmarkForm(forms.ModelForm):
    lists = forms.CharField(required=False)

    def clean_url(self):
        # django will add a trailing slash after a url, like "http://afaker.com" -> "http://afaker.com/"
        # here is to prevent the action to happend 
        return self.data['url'].strip()

    def clean_note(self):
        return self.data['note'].strip()

    class Meta:
        model = Bookmark
        fields = ['url', 'title', 'note', 'tags', 'domain']

class ListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):  
        super(ListForm, self).__init__(*args, **kwargs)
        

    class Meta:
        model = List
        fields = ['name', 'position', 'public', 'kind']

    def clean_kind(self):
        kind = self.cleaned_data.get("kind")
        if kind and self.instance.kind != kind:
            raise forms.ValidationError("not allowed to change this.")
        return kind

class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['text']

class FollowForm(forms.ModelForm):

    class Meta:
        model = Follow
        fields = []


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = [
            "comment"
        ]
    
    def clean(self):
        if self.instance:
            comment = self.instance
            comment.site_id = 1
        return self.cleaned_data

class ListInvitationForm(forms.ModelForm):

    class Meta:
        model = ListInvitation
        fields = ['status']
