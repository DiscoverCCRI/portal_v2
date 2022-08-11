from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from portal.apps.profiles.models import DiscoverUserCredential

class DiscoverUserCredentialForm(forms.ModelForm):
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Note',
    )

    publickey = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='New public key',
    )

    class Meta:
        model = DiscoverUserCredential
        fields = ('note', 'publickey')