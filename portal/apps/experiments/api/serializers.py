from rest_framework import serializers

from portal.apps.experiments.models import AerpawExperiment, UserExperiment


class UserExperimentSerializer(serializers.ModelSerializer):
    experiment_id = serializers.IntegerField(source='experiment.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserExperiment
        fields = ['granted_by', 'granted_date', 'experiment_id', 'id', 'user_id']


class ExperimentSerializerList(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_id',
                  'experiment_state', 'is_canonical', 'is_retired', 'name']


class ExperimentSerializerDetail(serializers.ModelSerializer):
    canonical_number = serializers.IntegerField(source='canonical_number.canonical_number')
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    project_id = serializers.IntegerField(source='project.id')
    experiment_members = UserExperimentSerializer(source='userexperiment_set', many=True)

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_id',
                  'experiment_members', 'experiment_state', 'is_canonical', 'is_retired', 'last_modified_by',
                  'modified_date', 'name', 'project_id', 'resources']
