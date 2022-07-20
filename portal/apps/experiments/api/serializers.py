from rest_framework import serializers

from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource, ExperimentSession, \
    UserExperiment


class UserExperimentSerializer(serializers.ModelSerializer):
    experiment_id = serializers.IntegerField(source='experiment.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserExperiment
        fields = ['granted_by', 'granted_date', 'experiment_id', 'id', 'user_id']


class ExperimentSerializerList(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_uuid = serializers.CharField(source='uuid')

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_id',
                  'experiment_uuid', 'experiment_state', 'is_canonical', 'is_retired', 'name', 'project_id']


class ExperimentSerializerDetail(serializers.ModelSerializer):
    canonical_number = serializers.IntegerField(source='canonical_number.canonical_number')
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_uuid = serializers.CharField(source='uuid')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    project_id = serializers.IntegerField(source='project.id')
    experiment_membership = UserExperimentSerializer(source='userexperiment_set', many=True)

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_id',
                  'experiment_uuid', 'experiment_membership', 'experiment_state', 'is_canonical', 'is_retired',
                  'last_modified_by', 'modified_date', 'name', 'project_id', 'resources']


class ExperimentSessionSerializer(serializers.ModelSerializer):
    ended_by = serializers.IntegerField(source='ended_by.id')
    experiment_id = serializers.IntegerField(source='experiment.id')
    session_id = serializers.IntegerField(source='id')
    start_date_time = serializers.DateTimeField(source='created')
    started_by = serializers.IntegerField(source='started_by.id')

    class Meta:
        model = ExperimentSession
        fields = ['end_date_time', 'ended_by', 'experiment_id', 'session_id', 'session_type',
                  'start_date_time', 'started_by']


class CanonicalExperimentResourceSerializer(serializers.ModelSerializer):
    canonical_experiment_resource_id = serializers.IntegerField(source='id')
    experiment_id = serializers.IntegerField(source='experiment.id')
    resource_id = serializers.IntegerField(source='resource.id')

    class Meta:
        model = CanonicalExperimentResource
        fields = ['canonical_experiment_resource_id', 'experiment_id', 'experiment_node_number', 'node_type',
                  'node_uhd', 'node_vehicle', 'resource_id']
