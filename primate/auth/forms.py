from django.contrib import auth
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class PassWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(u'<input type="button" value="%s" onclick="window.location.href=\'password/\'">' % _('Change Password'))


class UserChangeForm(auth.forms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = PassWidget()

