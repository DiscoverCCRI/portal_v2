from rest_framework import serializers

from portal.apps.operations.models import CanonicalNumber


class CanonicalNumberSerializerList(serializers.ModelSerializer):
    canonical_number_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CanonicalNumber
        fields = ['canonical_number', 'canonical_number_id', 'timestamp']


class CanonicalNumberSerializerDetail(serializers.ModelSerializer):
    canonical_number_id = serializers.IntegerField(source='id', read_only=True)
    created_date = serializers.DateTimeField(source='created')
    modified_date = serializers.DateTimeField(source='modified')

    class Meta:
        model = CanonicalNumber
        fields = ['canonical_number', 'canonical_number_id', 'created_date', 'is_deleted',
                  'is_retired', 'modified_date', 'timestamp']
