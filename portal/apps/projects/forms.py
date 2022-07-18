from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from portal.apps.projects.models import AerpawProject
from portal.apps.users.models import AerpawUser


class ProjectCreateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Name',
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=True,
        label='Description',
    )

    class Meta:
        model = AerpawProject
        fields = ['name', 'description', 'is_public']


class ProjectMembershipForm(forms.ModelForm):
    project_members = forms.ModelMultipleChoiceField(
        queryset=AerpawUser.objects.all().order_by('display_name'),
        widget=FilteredSelectMultiple('Members', is_stacked=False),
        required=False
    )

    project_owners = forms.ModelMultipleChoiceField(
        queryset=AerpawUser.objects.all().order_by('display_name'),
        widget=FilteredSelectMultiple('Owners', is_stacked=False),
        required=False
    )

    class Media:
        extend = False
        css = {
            'all': [
                'admin/css/widgets.css'
            ]
        }
        js = (
            'js/django_global.js',
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'admin/js/prepopulate_init.js',
            'admin/js/prepopulate.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )

    class Meta:
        model = AerpawProject
        fields = ['project_members', 'project_owners']
