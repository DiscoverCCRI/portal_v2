from django.db.models import Q
from uuid import uuid4

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError, MethodNotAllowed
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.projects.api.serializers import ProjectSerializerList, ProjectSerializerDetail, UserProjectSerializer
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

    def get_project_queryset(self, user: AerpawUser):
        search = self.request.query_params.get('search', None)
        if search:
            queryset = AerpawProject.objects.filter(
                Q(name__icontains=search) &
                (Q(is_public=True) |
                 Q(project_personnel__email__in=[user.email]) |
                 Q(project_creator=user))
            ).order_by('name')
        else:
            queryset = AerpawProject.objects.filter(
                Q(is_public=True) |
                Q(project_personnel__email__in=[user.email]) |
                Q(project_creator=user)
            ).order_by('name')
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
            page = self.paginate_queryset(self.get_project_queryset(request.user))
            if page:
                serializer = ProjectSerializerList(page, many=True)
            else:
                serializer = ProjectSerializerList(self.get_project_queryset(request.user), many=True)
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
            print(du)
            project_members = []
            project_owners = []
            for p in du.get('project_personnel'):
                person = {
                    'granted_by': p.get('granted_by'),
                    'granted_date': str(p.get('granted_date')),
                    'user_id': p.get('user_id')
                }
                if p.get('project_role') == UserProject.RoleType.PROJECT_MEMBER:
                    project_members.append(person)
                if p.get('project_role') == UserProject.RoleType.PROJECT_OWNER:
                    project_owners.append(person)
            response_data = {
                'created_date': str(du.get('created_date')),
                'description': du.get('description'),
                'is_public': du.get('is_public'),
                'last_modified_by': du.get('last_modified_by'),
                'modified_date': str(du.get('modified_date')),
                'name': du.get('name'),
                'project_creator': du.get('project_creator'),
                'project_id': du.get('project_id'),
                'project_members': project_members,
                'project_owners': project_owners
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


class UserProjectViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    UserProject
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProject.objects.all().order_by('-granted_date')
    serializer_class = UserProjectSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id', None)
        user_id = self.request.query_params.get('user_id', None)
        if project_id and user_id:
            queryset = UserProject.objects.filter(
                project__id=project_id,
                user__id=user_id
            ).order_by('-granted_date')
        elif project_id:
            queryset = UserProject.objects.filter(
                project__id=project_id
            ).order_by('-granted_date')
        elif user_id:
            queryset = UserProject.objects.filter(
                user__id=user_id
            ).order_by('-granted_date')
        else:
            queryset = UserProject.objects.filter().order_by('-granted_date')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list user-project as paginated results
        - granted_by             - int
        - granted_date           - string
        - id                     - int
        - project_id             - int
        - project_role           - string
        - user_id                - int

        Permission:
        - user is_operator
        """
        if request.user.is_operator():
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = UserProjectSerializer(page, many=True)
            else:
                serializer = UserProjectSerializer(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'granted_by': du.get('granted_by'),
                        'granted_date': du.get('granted_date'),
                        'id': du.get('id'),
                        'project_id': du.get('project_id'),
                        'project_role': du.get('project_role'),
                        'user_id': du.get('user_id')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /user-project list")

    def create(self, request):
        """
        POST: user cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /user-project")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: user-project as detailed result
        - granted_by             - int
        - granted_date           - string
        - id                     - int
        - project_id             - int
        - project_role           - string
        - user_id                - int

        Permission:
        - user is_operator
        """
        user_project = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            serializer = UserProjectSerializer(user_project)
            du = dict(serializer.data)
            response_data = {
                'granted_by': du.get('granted_by'),
                'granted_date': du.get('granted_date'),
                'id': du.get('id'),
                'project_id': du.get('project_id'),
                'project_role': du.get('project_role'),
                'user_id': du.get('user_id')
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /user-project/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: user-project cannot be updated via the API
        """
        raise MethodNotAllowed(method="PUT/PATCH: /user-project/{user_id}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: user-project cannot be updated via the API
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: user-project cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /user-project/{user_id}")
