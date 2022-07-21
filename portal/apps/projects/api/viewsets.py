from uuid import uuid4

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.experiments.api.serializers import ExperimentSerializerDetail
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.projects.api.serializers import ProjectSerializerDetail, ProjectSerializerList, UserProjectSerializer
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
    - experiments
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawProject.objects.all().order_by('name').distinct()
    serializer_class = ProjectSerializerList

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        user = self.request.user
        if search:
            if user.is_operator():
                queryset = AerpawProject.objects.filter(
                    is_deleted=False, name__icontains=search).order_by('name').distinct()
            else:
                queryset = AerpawProject.objects.filter(
                    Q(is_deleted=False, name__icontains=search) &
                    (Q(is_public=True) | Q(project_membership__email__in=[user.email]) | Q(project_creator=user))
                ).order_by('name').distinct()
        else:
            if user.is_operator():
                queryset = AerpawProject.objects.filter(is_deleted=False).order_by('name').distinct()
            else:
                queryset = AerpawProject.objects.filter(
                    Q(is_deleted=False) &
                    (Q(is_public=True) | Q(project_membership__email__in=[user.email]) | Q(project_creator=user))
                ).order_by('name').distinct()
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
                # add project membership
                project = AerpawProject.objects.get(pk=du.get('project_id'))
                is_project_creator = project.is_creator(request.user)
                is_project_member = project.is_member(request.user)
                is_project_owner = project.is_owner(request.user)
                response_data.append(
                    {
                        'created_date': du.get('created_date'),
                        'description': du.get('description'),
                        'is_public': du.get('is_public'),
                        'membership': {
                            'is_project_creator': is_project_creator,
                            'is_project_member': is_project_member,
                            'is_project_owner': is_project_owner
                        },
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
            # validate description
            description = request.data.get('description', None)
            if not description or len(description) < PROJECT_MIN_DESC_LEN:
                raise ValidationError(
                    detail="description:  must be at least {0} chars long".format(PROJECT_MIN_DESC_LEN))
            # validate is_pubic
            is_public = str(request.data.get('is_public')).casefold() == 'true'
            # validate name
            name = request.data.get('name', None)
            if not name or len(name) < PROJECT_MIN_NAME_LEN:
                raise ValidationError(
                    detail="name: must be at least {0} chars long".format(PROJECT_MIN_NAME_LEN))
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
            membership = UserProject()
            membership.granted_by = user
            membership.project = project
            membership.project_role = UserProject.RoleType.PROJECT_OWNER
            membership.user = user
            membership.save()
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
        - user is_creator OR
        - user is_project_member OR
        - user is_project_owner OR
        - user is_operator
        """
        project = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            serializer = ProjectSerializerDetail(project)
            du = dict(serializer.data)
            project_members = []
            project_owners = []
            for p in du.get('project_membership'):
                person = {
                    'granted_by': p.get('granted_by'),
                    'granted_date': str(p.get('granted_date')),
                    'user_id': p.get('user_id')
                }
                if p.get('project_role') == UserProject.RoleType.PROJECT_MEMBER:
                    project_members.append(person)
                if p.get('project_role') == UserProject.RoleType.PROJECT_OWNER:
                    project_owners.append(person)
            # add project membership
            is_project_creator = project.is_creator(request.user)
            is_project_member = project.is_member(request.user)
            is_project_owner = project.is_owner(request.user)
            response_data = {
                'created_date': str(du.get('created_date')),
                'description': du.get('description'),
                'is_public': du.get('is_public'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'membership': {
                    'is_project_creator': is_project_creator,
                    'is_project_member': is_project_member,
                    'is_project_owner': is_project_owner
                },
                'modified_date': str(du.get('modified_date')),
                'name': du.get('name'),
                'project_creator': du.get('project_creator'),
                'project_id': du.get('project_id'),
                'project_members': project_members,
                'project_owners': project_owners
            }
            if project.is_deleted:
                response_data['is_deleted'] = du.get('is_deleted')
            return Response(response_data)
        elif request.user.is_active:
            if project.is_public:
                serializer = ProjectSerializerDetail(project)
                du = dict(serializer.data)
                # add project membership
                is_project_creator = project.is_creator(request.user)
                is_project_member = project.is_member(request.user)
                is_project_owner = project.is_owner(request.user)
                response_data = {
                    'created_date': du.get('created_date'),
                    'description': du.get('description'),
                    'is_public': du.get('is_public'),
                    'membership': {
                        'is_project_creator': is_project_creator,
                        'is_project_member': is_project_member,
                        'is_project_owner': is_project_owner
                    },
                    'name': du.get('name'),
                    'project_creator': du.get('project_creator'),
                    'project_id': du.get('project_id')
                }
                if project.is_deleted:
                    response_data['is_deleted'] = du.get('is_deleted')
            else:
                response_data = {}
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
        - user is_project_creator OR
        - user is_project_owner
        """
        project = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if not project.is_deleted and (project.is_creator(request.user) or project.is_owner(request.user)):
            modified = False
            # check for description
            if request.data.get('description', None):
                if len(request.data.get('description')) < PROJECT_MIN_DESC_LEN:
                    raise ValidationError(
                        detail="description:  must be at least {0} chars long".format(PROJECT_MIN_DESC_LEN))
                project.description = request.data.get('description')
                modified = True
            # check for is_public
            if str(request.data.get('is_public')).casefold() in ['true', 'false']:
                is_public = str(request.data.get('is_public')).casefold() == 'true'
                project.is_public = is_public
                modified = True
            # check for name
            if request.data.get('name', None):
                if len(request.data.get('name')) < PROJECT_MIN_NAME_LEN:
                    raise ValidationError(
                        detail="name: must be at least {0} chars long".format(PROJECT_MIN_NAME_LEN))
                project.name = request.data.get('name')
                modified = True
            # save if modified
            if modified:
                project.modified_by = request.user.email
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
        DELETE: soft delete existing project
        - is_deleted             - bool

        Permission:
        - user is_project_creator
        """
        project = get_object_or_404(self.queryset, pk=pk)
        if project.is_creator(request.user):
            project.is_deleted = True
            project.modified_by = request.user.username
            project.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to DELETE /projects/{0}".format(pk))

    @action(detail=True, methods=['get'])
    def experiments(self, request, *args, **kwargs):
        """
        GET: list experiments as paginated results
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - user_ID
        - experiment_id          - int
        - experiment_uuid        - string
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string

        Permission:
        - user is_project_creator OR
        - user is_project_member OR
        - user is_project_owner OR
        - user is_operator
        """
        project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            experiments = AerpawExperiment.objects.filter(project__id=project.id).order_by('name').distinct()
            serializer = ExperimentSerializerDetail(experiments, many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'canonical_number': du.get('canonical_number'),
                        'created_date': du.get('created_date'),
                        'description': du.get('description'),
                        'experiment_creator': du.get('experiment_creator'),
                        'experiment_id': du.get('experiment_id'),
                        'experiment_uuid': du.get('experiment_uuid'),
                        'is_canonical': du.get('is_canonical'),
                        'is_retired': du.get('is_retired'),
                        'name': du.get('name')
                    }
                )
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /projects/{0}/experiments".format(kwargs.get('pk')))

    @action(detail=True, methods=['get', 'put', 'patch'])
    def membership(self, request, *args, **kwargs):
        """
        GET, PUT, PATCH: list / update experiment members
        - project_members        - array of user-experiment
        - project_owners         - array of user-experiment

        Permission:
        - user is_project_creator OR
        - user is_project_owner
        """
        project = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if project.is_creator(request.user) or project.is_owner(request.user):
            if str(request.method).casefold() in ['put', 'patch']:
                if request.data.get('project_members') or isinstance(request.data.get('project_members'), list):
                    project_members = request.data.get('project_members')
                    if isinstance(project_members, list) and all([isinstance(item, int) for item in project_members]):
                        project_members_orig = UserProject.objects.filter(
                            project__id=project.id,
                            project_role=UserProject.RoleType.PROJECT_MEMBER
                        ).values_list('user__id', flat=True)
                        project_members_added = list(set(project_members).difference(set(project_members_orig)))
                        project_members_removed = list(set(project_members_orig).difference(set(project_members)))
                        for pk in project_members_added:
                            if AerpawUser.objects.filter(pk=pk).exists():
                                user = AerpawUser.objects.get(pk=pk)
                                # experimenter or pi roles only
                                if user.is_experimenter() or user.is_pi():
                                    membership = UserProject()
                                    membership.granted_by = request.user
                                    membership.project = project
                                    membership.project_role = UserProject.RoleType.PROJECT_MEMBER
                                    membership.user = user
                                    membership.save()
                        for pk in project_members_removed:
                            membership = UserProject.objects.get(
                                project__id=project.id, user__id=pk, project_role=UserProject.RoleType.PROJECT_MEMBER)
                            membership.delete()
                if request.data.get('project_owners') or isinstance(request.data.get('project_owners'), list):
                    project_owners = request.data.get('project_owners')
                    if isinstance(project_owners, list) and all([isinstance(item, int) for item in project_owners]):
                        project_owners_orig = UserProject.objects.filter(
                            project__id=project.id,
                            project_role=UserProject.RoleType.PROJECT_OWNER
                        ).values_list('user__id', flat=True)
                        project_owners_added = list(set(project_owners).difference(set(project_owners_orig)))
                        project_owners_removed = list(set(project_owners_orig).difference(set(project_owners)))
                        for pk in project_owners_added:
                            if AerpawUser.objects.filter(pk=pk).exists():
                                user = AerpawUser.objects.get(pk=pk)
                                # experimenter or pi roles only
                                if user.is_experimenter() or user.is_pi():
                                    membership = UserProject()
                                    membership.granted_by = request.user
                                    membership.project = project
                                    membership.project_role = UserProject.RoleType.PROJECT_OWNER
                                    membership.user = user
                                    membership.save()
                        for pk in project_owners_removed:
                            membership = UserProject.objects.get(
                                project__id=project.id, user__id=pk, project_role=UserProject.RoleType.PROJECT_OWNER)
                            membership.delete()
            # End of PUT, PATCH section - All reqeust types return membership
            serializer = ProjectSerializerDetail(project)
            du = dict(serializer.data)
            project_members = []
            project_owners = []
            for p in du.get('project_membership'):
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
                'project_members': project_members,
                'project_owners': project_owners
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET,PUT,PATCH /projects/{0}/membership".format(kwargs.get('pk')))


class UserProjectViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    UserProject
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProject.objects.all().order_by('-granted_date').distinct()
    serializer_class = UserProjectSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id', None)
        user_id = self.request.query_params.get('user_id', None)
        if project_id and user_id:
            queryset = UserProject.objects.filter(
                project__id=project_id,
                user__id=user_id
            ).order_by('-granted_date').distinct()
        elif project_id:
            queryset = UserProject.objects.filter(
                project__id=project_id
            ).order_by('-granted_date').distinct()
        elif user_id:
            queryset = UserProject.objects.filter(
                user__id=user_id
            ).order_by('-granted_date').distinct()
        else:
            queryset = UserProject.objects.filter().order_by('-granted_date').distinct()
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
        POST: user-project cannot be created via the API
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
        raise MethodNotAllowed(method="PUT/PATCH: /user-project/{int:pk}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: user-project cannot be updated via the API
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: user-project cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /user-project/{int:pk}")
