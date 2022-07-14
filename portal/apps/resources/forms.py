from django import forms

from portal.apps.resources.models import AerpawResource


class ResourceCreateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Name',
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Description',
    )

    hostname = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        required=False,
        label='Hostname',
    )

    ip_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        required=False,
        label='IP Address',
    )

    location = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        required=False,
        label='Location',
    )

    ops_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Operator Notes',
    )

    resource_class = forms.ChoiceField(
        choices=AerpawResource.ResourceClass.choices,
        widget=forms.Select(),
        required=False,
        label='Class',
    )

    resource_mode = forms.ChoiceField(
        choices=AerpawResource.ResourceMode.choices,
        widget=forms.Select(),
        required=False,
        label='Mode',
    )

    resource_type = forms.ChoiceField(
        choices=AerpawResource.ResourceType.choices,
        widget=forms.Select(),
        required=False,
        label='Type',
    )

    class Meta:
        model = AerpawResource
        fields = ['name', 'description', 'hostname', 'ip_address', 'location', 'resource_class', 'resource_mode',
                  'resource_type', 'ops_notes', 'is_active']
