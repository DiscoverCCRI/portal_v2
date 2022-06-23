from uuid import uuid4

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.resources.api.serializers import ResourceSerializerDetail, ResourceSerializerList
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser

# constants
RESOURCE_MIN_NAME_LEN = 5
RESOURCE_MIN_DESC_LEN = 5
RESOURCE_MIN_HOSTNAME_LEN = 5
RESOURCE_MIN_LOCATION_LEN = 3


class ResourceViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Resource
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    - experiments
    - projects
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawResource.objects.all().order_by('name')
    serializer_class = ResourceSerializerDetail

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        if search:
            queryset = AerpawResource.objects.filter(
                Q(is_deleted=False) & (Q(name__icontains=search) | Q(resource_type__icontains=search))
            ).order_by('name')
        else:
            queryset = AerpawResource.objects.filter(is_deleted=False).order_by('name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list resources as paginated results
        - description            - string
        - is_active              - boolean
        - location               - string
        - name                   - string
        - resource_class         - string
        - resource_id            - int
        - resource_mode          - string
        - resource_type          - string

        Permission:
        - user is_active
        """
        if request.user.is_active:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ResourceSerializerList(page, many=True)
            else:
                serializer = ResourceSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'description': du.get('description'),
                        'is_active': du.get('is_active'),
                        'location': du.get('location'),
                        'name': du.get('name'),
                        'resource_class': du.get('resource_class'),
                        'resource_id': du.get('resource_id'),
                        'resource_mode': du.get('resource_mode'),
                        'resource_type': du.get('resource_type')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /resources list")

    def create(self, request):
        """
        POST: resource as detailed result
        - created_by             - int
        - created_date           - string
        - description            - string
        - hostname               - string
        - ip_address             - string
        - is_active              - boolean
        - location               - string
        - name                   - string
        - ops_notes              - string
        - resource_class         - string
        - resource_id            - int
        - resource_mode          - string
        - resource_type          - string

        Permission:
        - user is_operator
        """
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if request.user.is_operator():
            # validate description
            description = request.data.get('description', None)
            if not description or len(description) < RESOURCE_MIN_DESC_LEN:
                raise ValidationError(
                    detail="description:  must be at least {0} chars long".format(RESOURCE_MIN_DESC_LEN))
            # validate hostname
            hostname = request.data.get('hostname', None)
            if not hostname or len(hostname) < RESOURCE_MIN_HOSTNAME_LEN:
                raise ValidationError(
                    detail="hostname:  must be at least {0} chars long".format(RESOURCE_MIN_HOSTNAME_LEN))
            # validate ip_address
            ip_address = request.data.get('ip_address', None)
            # validate is_active
            is_active = str(request.data.get('is_active')).casefold() == 'true'
            # validate location
            location = request.data.get('location', None)
            if not location or len(location) < RESOURCE_MIN_LOCATION_LEN:
                raise ValidationError(
                    detail="location:  must be at least {0} chars long".format(RESOURCE_MIN_LOCATION_LEN))
            # validate name
            name = request.data.get('name', None)
            if not name or len(name) < RESOURCE_MIN_NAME_LEN:
                raise ValidationError(
                    detail="name: must be at least {0} chars long".format(RESOURCE_MIN_NAME_LEN))
            # validate ops_notes
            ops_notes = request.data.get('ops_notes', None)
            # validate resource_class
            resource_class = request.data.get('resource_class', None)
            if resource_class not in [c[0] for c in AerpawResource.ResourceClass.choices]:
                raise ValidationError(
                    detail="resource_class: must be a valid Resource Class value")
            # validate resource_mode
            resource_mode = request.data.get('resource_mode', None)
            if resource_mode not in [c[0] for c in AerpawResource.ResourceMode.choices]:
                raise ValidationError(
                    detail="resource_mode: must be a valid Resource Mode value")
            # validate resource_type
            resource_type = request.data.get('resource_type', None)
            if resource_type not in [c[0] for c in AerpawResource.ResourceType.choices]:
                raise ValidationError(
                    detail="resource_class: must be a valid Resource Type value")
            # create resource
            resource = AerpawResource()
            resource.created_by = user.username
            resource.description = description
            resource.hostname = hostname
            resource.ip_address = ip_address
            resource.is_active = is_active
            resource.location = location
            resource.modified_by = user.username
            resource.name = name
            resource.ops_notes = ops_notes
            resource.resource_class = resource_class
            resource.resource_mode = resource_mode
            resource.resource_type = resource_type
            resource.uuid = uuid4()
            resource.save()
            return self.retrieve(request, pk=resource.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to POST /resources")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: resource as detailed result
        - created_date           - string
        - description            - string
        - hostname               - string
        - ip_address             - string
        - is_active              - boolean
        - location               - string
        - last_modified_by (fk)  - user_ID
        - modified_date          - string
        - name                   - string
        - ops_notes              - string
        - resource_class         - string
        - resource_creator (fk)  - user_ID
        - resource_id            - int
        - resource_mode          - string
        - resource_type          - string

        Permission:
        - user is_active
        """
        resource = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_active:
            serializer = ResourceSerializerDetail(resource)
            du = dict(serializer.data)
            response_data = {
                'created_date': str(du.get('created_date')),
                'description': du.get('description'),
                'hostname': du.get('hostname'),
                'ip_address': du.get('ip_address'),
                'is_active': du.get('is_active'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'location': du.get('location'),
                'modified_date': du.get('modified_date'),
                'name': du.get('name'),
                'ops_notes': du.get('ops_notes'),
                'resource_class': du.get('resource_class'),
                'resource_creator': AerpawUser.objects.get(username=du.get('resource_creator')).id,
                'resource_id': du.get('resource_id'),
                'resource_mode': du.get('resource_mode'),
                'resource_type': du.get('resource_type')
            }
            if resource.is_deleted:
                response_data['is_deleted'] = du.get('is_deleted')
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /resources/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing resource
        - description            - string
        - hostname               - string
        - ip_address             - string
        - is_active              - boolean
        - location               - string
        - modified_by            - string
        - name                   - string
        - ops_notes              - string
        - resource_class         - string
        - resource_id            - int
        - resource_mode          - string
        - resource_type          - string

        Permission:
        - user is_operator
        """
        resource = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if not resource.is_deleted and request.user.is_operator():
            modified = False
            # check for description
            if request.data.get('description', None):
                if len(request.data.get('description')) < RESOURCE_MIN_DESC_LEN:
                    raise ValidationError(
                        detail="description:  must be at least {0} chars long".format(RESOURCE_MIN_DESC_LEN))
                resource.description = request.data.get('description')
                modified = True
            # check for hostname
            if request.data.get('hostname', None):
                if len(request.data.get('hostname')) < RESOURCE_MIN_HOSTNAME_LEN:
                    raise ValidationError(
                        detail="hostname:  must be at least {0} chars long".format(RESOURCE_MIN_HOSTNAME_LEN))
                resource.hostname = request.data.get('hostname')
                modified = True
            # check for ip_address
            if request.data.get('ip_address', None):
                resource.ip_address = request.data.get('ip_address')
                modified = True
            # check for is_active
            if str(request.data.get('is_active')).casefold() in ['true', 'false']:
                is_active = str(request.data.get('is_active')).casefold() == 'true'
                resource.is_active = is_active
                modified = True
            # check for location
            if request.data.get('location', None):
                if len(request.data.get('location')) < RESOURCE_MIN_LOCATION_LEN:
                    raise ValidationError(
                        detail="location:  must be at least {0} chars long".format(RESOURCE_MIN_LOCATION_LEN))
                resource.location = request.data.get('location')
                modified = True
            # check for name
            if request.data.get('name', None):
                if len(request.data.get('name')) < RESOURCE_MIN_NAME_LEN:
                    raise ValidationError(
                        detail="name:  must be at least {0} chars long".format(RESOURCE_MIN_NAME_LEN))
                resource.name = request.data.get('name')
                modified = True
            # check for ops_notes
            if request.data.get('ops_notes', None):
                resource.ops_notes = request.data.get('ops_notes')
                modified = True
            # validate resource_class
            if request.data.get('resource_class', None):
                if request.data.get('resource_class') not in [c[0] for c in AerpawResource.ResourceClass.choices]:
                    raise ValidationError(
                        detail="resource_class: must be a valid Resource Class value")
                resource.resource_class = request.data.get('resource_class')
                modified = True
            # check for resource_mode
            if request.data.get('resource_mode', None):
                if request.data.get('resource_mode') not in [c[0] for c in AerpawResource.ResourceMode.choices]:
                    raise ValidationError(
                        detail="resource_mode: must be a valid Resource Mode value")
                resource.resource_mode = request.data.get('resource_mode')
                modified = True
            # check for resource_type
            if request.data.get('resource_type', None):
                if request.data.get('resource_type') not in [c[0] for c in AerpawResource.ResourceType.choices]:
                    raise ValidationError(
                        detail="resource_class: must be a valid Resource Type value")
                resource.resource_type = request.data.get('resource_type', None)
                modified = True
            # save if modified
            if modified:
                resource.modified_by = request.user.email
                resource.save()
            return self.retrieve(request, pk=resource.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /resources/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing resource
        - description            - string
        - hostname               - string
        - ip_address             - string
        - is_active              - boolean
        - location               - string
        - name                   - string
        - ops_notes              - string
        - resource_class         - string
        - resource_id            - int
        - resource_mode          - string
        - resource_type          - string

        Permission:
        - user is_operator
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing project
        - is_deleted             - bool

        Permission:
        - user is_resource_creator
        """
        resource = get_object_or_404(self.queryset, pk=pk)
        if resource.created_by == request.user.username:
            resource.is_active = False
            resource.is_deleted = True
            resource.modified_by = request.user.username
            resource.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to DELETE /resources/{0}".format(pk))

    @action(detail=True, methods=['get'])
    def experiments(self, request, *args, **kwargs):
        """
        GET: list experiments as paginated results
        - description            - string
        - experiment_creator     - user_ID
        - experiment_id          - int
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string

        Permission:
        - user is_operator
        """
        resource = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            # TODO: experiments serializer and response
            response_data = {}
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /resources/{0}/experiments".format(kwargs.get('pk')))

    @action(detail=True, methods=['get'])
    def projects(self, request, *args, **kwargs):
        """
        GET: list projects as paginated results
        - created_date           - UTC timestamp
        - description            - string
        - is_public              - bool
        - name                   - string
        - project_creator (fk)   - user_ID
        - project_id (pk)        - integer

        Permission:
        - user is_operator
        """
        resource = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            # TODO: projects serializer and response
            response_data = {}
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /resources/{0}/projects".format(kwargs.get('pk')))
