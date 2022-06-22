from uuid import uuid4

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.projects.api.serializers import ProjectSerializerList, ProjectSerializerDetail
from portal.apps.projects.models import AerpawProject, UserProject
from portal.apps.users.models import AerpawUser

# constants
PROJECT_MIN_NAME_LEN = 5
PROJECT_MIN_DESC_LEN = 5


class ProjectViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    AERPAW Projects
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawProject.objects.all().order_by('name')
    serializer_class = ProjectSerializerList

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        if search:
            queryset = AerpawProject.objects.filter(
                name__icontains=search
            ).order_by('name')
        else:
            queryset = AerpawProject.objects.all().order_by('name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list projects as paginated results
        - created_date           - UTC timestamp
        - description            - string
        - is_public              - bool
        - name                   - string
        - project_creator (fk)   - user_ID
        - project_id (pk)        - integer

        Permission:
        - active users
        """
        if request.user.is_active:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ProjectSerializerList(page, many=True)
            else:
                serializer = ProjectSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'created_date': du.get('created_date'),
                        'description': du.get('description'),
                        'is_public': du.get('is_public'),
                        'name': du.get('name'),
                        'project_creator': du.get('project_creator'),
                        'project_id': du.get('project_id')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /projects list")

    def create(self, request):
        """
        POST: create a new project
        - description            - string
        - is_public              - bool
        - name                   - string

        Permission:
        - user is_pi
        """
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if request.user.is_pi():
            # validate name
            name = request.data.get('name', None)
            if not name or len(name) < PROJECT_MIN_NAME_LEN:
                raise ValidationError(
                    detail="name: must be at least {0} chars long".format(PROJECT_MIN_NAME_LEN))
            # validate description
            description = request.data.get('description', None)
            if not description or len(description) < PROJECT_MIN_DESC_LEN:
                raise ValidationError(
                    detail="description:  must be at least {0} chars long".format(PROJECT_MIN_DESC_LEN))
            # check is_pubic
            is_public = str(request.data.get('is_public')).casefold() == 'true'
            # create project
            project = AerpawProject()
            project.created_by = user.username
            project.project_creator = user
            project.description = description
            project.is_public = is_public
            project.modified_by = user.username
            project.name = name
            project.uuid = uuid4()
            project.save()
            # set creator as project_owner
            personnel = UserProject()
            personnel.granted_by = user
            personnel.project = project
            personnel.project_role = UserProject.RoleType.PROJECT_OWNER
            personnel.user = user
            personnel.save()
            return self.retrieve(request, pk=project.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to POST /projects")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve project as single result
        - created_date           - UTC timestamp
        - description            - string
        - is_public              - bool
        - last_modified_by (fk)  - user_ID
        - modified_date          - UTC timestamp
        - name                   - string
        - project_creator (fk)   - user_ID
        - project_id (pk)        - integer
        - project_members (fk)   - array of integer
        - project_owners (fk)    - array of integer

        Permission:
        - user is_creator
        - user is_project_member
        - user is_project_owner
        - user is_operator
        """
        project = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            serializer = ProjectSerializerDetail(project)
            du = dict(serializer.data)
            response_data = {
                'created_date': str(du.get('created_date')),
                'description': du.get('description'),
                'is_public': du.get('is_public'),
                'last_modified_by': du.get('last_modified_by'),
                'modified_date': str(du.get('modified_date')),
                'name': du.get('name'),
                'project_creator': du.get('project_creator'),
                'project_id': du.get('project_id'),
                'project_members': [p.get('user_id') for p in du.get('project_personnel') if
                                   p.get('role') == UserProject.RoleType.PROJECT_MEMBER],
                'project_owners': [p.get('user_id') for p in du.get('project_personnel') if
                                   p.get('role') == UserProject.RoleType.PROJECT_OWNER]
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /projects/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing project
        - description            - string
        - is_public              - bool
        - name                   - string

        Permission:
        - user is_project_creator
        - user is_project_owner
        """
        project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_owner(request.user):
            print(request.data)
            # check for description
            if request.data.get('description', None):
                project.description = request.data.get('description')
                project.modified_by = request.user.email
                project.save()
            # check for is_public
            if str(request.data.get('is_public')).casefold() in ['true', 'false']:
                is_public = str(request.data.get('is_public')).casefold() == 'true'
                project.modified_by = request.user.email
                project.is_public = is_public
                project.save()
            # check for name
            if request.data.get('name', None):
                project.modified_by = request.user.email
                project.name = request.data.get('name')
                project.save()
            return self.retrieve(request, pk=project.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /projects/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing project
        - description            - string
        - is_public              - bool
        - name                   - string

        Permission:
        - user is_project_creator
        - user is_project_owner
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: project cannot be deleted via the API
        """
        raise PermissionDenied(detail="project deletion is not supported via API")

    @action(detail=True, methods=['get'])
    def experiments(self, request, *args, **kwargs):
        """
        GET: experiments
        - name                   - string
        - public_key_credential  - string
        - public_key_id          - int

        Permission:
        - user is_project_creator
        - user is_project_member
        - user is_project_owner
        - user is_operator
        """
        project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            # TODO: experiments serializer and response
            response_data = {}
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /projects/{0}/experiments".format(kwargs.get('pk')))
