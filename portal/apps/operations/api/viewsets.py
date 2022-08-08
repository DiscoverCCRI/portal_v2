from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.operations.api.serializers import CanonicalNumberSerializerDetail, CanonicalNumberSerializerList
from portal.apps.operations.models import CanonicalNumber, get_current_canonical_number, set_current_canonical_number


class CanonicalNumberViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Canonical Number
    - paginated list
    - retrieve one
    - current
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CanonicalNumber.objects.all().order_by('-created')
    serializer_class = CanonicalNumberSerializerDetail

    def get_queryset(self):
        queryset = CanonicalNumber.objects.filter(is_deleted=False).order_by('-created')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list canonical-number as paginated results
        - canonical_number       - int
        - canonical_number_id    - int
        - created_date           - string
        - is_deleted             - bool
        - is_retired             - bool
        - modified_date          - string
        - timestamp              - int

        Permission:
        - user is_operator
        """
        if request.user.is_operator():
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = CanonicalNumberSerializerList(page, many=True)
            else:
                serializer = CanonicalNumberSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'canonical_number': du.get('canonical_number'),
                        'canonical_number_id': du.get('canonical_number_id'),
                        'timestamp': du.get('timestamp')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /canonical-number list")

    def create(self, request):
        """
        POST: canonical-number cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /canonical-number")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: canonical-number as detailed result
        - canonical_number       - int
        - canonical_number_id    - int
        - created_date           - string
        - is_deleted             - bool
        - is_retired             - bool
        - modified_date          - string
        - timestamp              - int

        Permission:
        - user is_operator
        """
        canonical_number = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            serializer = CanonicalNumberSerializerDetail(canonical_number)
            du = dict(serializer.data)
            response_data = {
                'canonical_number': du.get('canonical_number'),
                'canonical_number_id': du.get('canonical_number_id'),
                'created_date': du.get('created_date'),
                'is_deleted': du.get('is_deleted'),
                'is_retired': du.get('is_retired'),
                'modified_date': du.get('modified_date'),
                'timestamp': du.get('timestamp')
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /canonical-number/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: canonical-number cannot be updated via the API
        """
        raise MethodNotAllowed(method="PUT/PATCH: /canonical-number/{int:pk}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: canonical-number cannot be updated via the API
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: canonical-number cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /canonical-number/{int:pk}")

    @action(detail=False, methods=['get', 'put', 'patch'])
    def current(self, request, *args, **kwargs):
        """
        GET: current
        - current_canonical_number  - int

        Permission:
        - user is_active
        """
        new_number = self.request.query_params.get('number', None)
        if new_number:
            if request.user.is_site_admin():
                set_current_canonical_number(new_number)
                response_data = {'current_canonical_number': int(get_current_canonical_number())}
                return Response(response_data)
            else:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to PUT/PATCH /canonical-number")
        if request.user.is_active:
            response_data = {'current_canonical_number': int(get_current_canonical_number())}
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /canonical-number/current")
