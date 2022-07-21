from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from portal.apps.experiments.models import AerpawExperiment
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource


class ExperimentCreateForm(forms.ModelForm):
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

    project_id = forms.IntegerField(
        required=True,
        label='Project ID'
    )

    class Meta:
        model = AerpawExperiment
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['project_id'].widget = forms.HiddenInput()


class ExperimentEditForm(forms.ModelForm):
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
        model = AerpawExperiment
        fields = ['name', 'description', 'is_retired']


class ExperimentMembershipForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExperimentMembershipForm, self).__init__(*args, **kwargs)
        exp = kwargs.get('instance')
        project = AerpawProject.objects.get(id=int(exp.project_id))
        self.fields['experiment_members'].queryset = (project.project_owners() | project.project_members()).distinct()

    experiment_members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=FilteredSelectMultiple('Members', is_stacked=False),
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
        model = AerpawExperiment
        fields = ['experiment_members']


class ExperimentResourceDefinitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExperimentResourceDefinitionForm, self).__init__(*args, **kwargs)
        self.fields['experiment_resources'].queryset = AerpawResource.objects.filter(
            resource_class=AerpawResource.ResourceClass.ALLOW_CANONICAL, is_deleted=False).order_by('name')

    experiment_resources = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=FilteredSelectMultiple('Resources', is_stacked=False),
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
        model = AerpawResource
        fields = ['experiment_resources']
