from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from portal.apps.experiments.api.viewsets import CanonicalExperimentResourceViewSet, ExperimentViewSet
from portal.apps.experiments.forms import ExperimentCreateForm, ExperimentEditForm, ExperimentMembershipForm, \
    ExperimentResourceTargetsForm, ExperimentResourceTargetModifyForm
from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource
from portal.apps.projects.api.viewsets import ProjectViewSet
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
def experiment_list(request):
    message = None
    # TODO: request to join experiment
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        e = ExperimentViewSet(request=request)
        experiments = e.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if experiments.data:
            experiments = dict(experiments.data)
            prev_url = experiments.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = experiments.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(experiments.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        experiments = None
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'experiment_list.html',
                  {
                      'user': request.user,
                      'experiments': experiments,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def experiment_detail(request, experiment_id):
    message = None
    try:
        e = ExperimentViewSet(request=request)
        experiment = e.retrieve(request=request, pk=experiment_id).data
        if request.method == "POST":
            if request.POST.get('delete-experiment') == "true":
                exp = e.destroy(request=request, pk=experiment_id).data
                return redirect('experiment_list')
        # get canonical experiment resource definitions
        try:
            resources = []
            request.query_params = QueryDict('', mutable=True)
            request.query_params.update({'experiment_id': experiment_id})
            for res_id in experiment.get('resources'):
                request.query_params.update({'resource_id': res_id})
                r = CanonicalExperimentResourceViewSet(request=request)
                res = r.list(request=request)
                if res.data:
                    resources.append(res.data.get('results')[0])
        except Exception as exc:
            resources = []
            print(exc)
    except Exception as exc:
        message = exc
        resources = []
    return render(request,
                  'experiment_detail.html',
                  {
                      'user': request.user,
                      'experiment': experiment,
                      'resources': resources,
                      'message': message,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def experiment_create(request):
    message = None
    project = None
    if request.method == "POST":
        form = ExperimentCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                request.data.update(data_dict)
                e = ExperimentViewSet(request=request)
                request.data.update(data_dict)
                experiment = e.create(request=request).data
                return redirect('experiment_detail', experiment_id=experiment.get('experiment_id', 9999))
            except Exception as exc:
                message = exc
    else:
        project_id = request.GET.get('project_id')
        p = ProjectViewSet()
        project = p.retrieve(request=request, pk=project_id).data
        form = ExperimentCreateForm(initial={'project_id': project_id})
    return render(request,
                  'experiment_create.html',
                  {
                      'form': form,
                      'message': message,
                      'project': project
                  })


@csrf_exempt
@login_required
def experiment_edit(request, experiment_id):
    message = 'INFO: selecting IS_RETIRED will permanently disable the experiment'
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    p = ProjectViewSet()
    project = p.retrieve(request=request, pk=experiment.project.id).data
    if request.method == "POST":
        form = ExperimentEditForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_retired', '') == 'on':
                    data_dict.update({'is_retired': 'true'})
                else:
                    data_dict.update({'is_retired': 'false'})
                request.data.update(data_dict)
                e = ExperimentViewSet(request=request)
                request.data.update(data_dict)
                experiment = e.partial_update(request=request, pk=experiment_id)
                return redirect('experiment_detail', experiment_id=experiment_id)
            except Exception as exc:
                message = exc
    else:
        form = ExperimentEditForm(instance=experiment, initial={'project_id': project.get('project_id')})
    return render(request,
                  'experiment_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'project': project
                  })


@csrf_exempt
@login_required
def experiment_members(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    is_experiment_creator = experiment.is_creator(request.user)
    is_experiment_member = experiment.is_member(request.user)
    if request.method == "POST":
        form = ExperimentMembershipForm(request.POST, instance=experiment)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update(
                    {'experiment_members': [int(i) for i in request.POST.getlist('experiment_members')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                e = ExperimentViewSet(request=api_request)
                experiment = e.membership(request=api_request, pk=experiment_id)
                return redirect('experiment_detail', experiment_id=experiment_id)
            except Exception as exc:
                message = exc
    else:
        initial_dict = {
            'experiment_members': list(experiment.experiment_members())
        }
        form = ExperimentMembershipForm(instance=experiment, initial=initial_dict)
    return render(request,
                  'experiment_members.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member
                  })


@csrf_exempt
@login_required
def experiment_resource_list(request, experiment_id):
    message = 'INFO: Be sure to properly configure "Node UHD" and "Node Vehicle"'
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {'experiment_id': experiment_id}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        r = CanonicalExperimentResourceViewSet(request=request)
        resources = r.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if resources.data:
            resources = dict(resources.data)
            prev_url = resources.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = resources.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(resources.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        resources = None
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'experiment_resource_list.html',
                  {
                      'user': request.user,
                      'resources': resources,
                      'experiment_id': experiment_id,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def experiment_resource_targets(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    is_experiment_creator = experiment.is_creator(request.user)
    is_experiment_member = experiment.is_member(request.user)
    if request.method == "POST":
        form = ExperimentResourceTargetsForm(request.POST, instance=experiment)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update(
                    {'experiment_resources': [int(i) for i in request.POST.getlist('experiment_resources')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                e = ExperimentViewSet(request=api_request)
                exp = e.resources(request=api_request, pk=experiment_id)
                return redirect('experiment_resource_list', experiment_id=experiment_id)
            except Exception as exc:
                message = exc
    else:
        initial_dict = {
            'experiment_resources': list(experiment.resources.all().values_list('id', flat=True))
        }
        form = ExperimentResourceTargetsForm(instance=experiment, initial=initial_dict)
    return render(request,
                  'experiments/experiment_resource_targets.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member
                  })


@csrf_exempt
@login_required
def experiment_resource_target_edit(request, experiment_id, canonical_experiment_resource_id):
    message = None
    cer = get_object_or_404(CanonicalExperimentResource, id=canonical_experiment_resource_id)
    is_experiment_creator = cer.experiment.is_creator(request.user)
    is_experiment_member = cer.experiment.is_member(request.user)
    if request.method == "POST":
        form = ExperimentResourceTargetModifyForm(request.POST, instance=cer)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                if request.POST.get('node_uhd'):
                    api_request.data.update({'node_uhd': request.POST.get('node_uhd')})
                if request.POST.get('node_vehicle'):
                    api_request.data.update({'node_vehicle': request.POST.get('node_vehicle')})
                api_request.user = request.user
                api_request.method = 'PUT'
                c = CanonicalExperimentResourceViewSet(request=api_request)
                u_cer = c.update(request=api_request, pk=canonical_experiment_resource_id)
                return redirect('experiment_resource_list', experiment_id=experiment_id)
            except Exception as exc:
                message = exc
    else:
        initial_dict = {
            'name': cer.resource.name,
            'node_type': cer.node_type,
            'node_uhd': cer.node_uhd,
            'node_vehicle': cer.node_vehicle
        }
        form = ExperimentResourceTargetModifyForm(instance=cer, initial=initial_dict)
    return render(request,
                  'experiment_resource_target_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'canonical_experiment_resource_id': canonical_experiment_resource_id,
                      'experiment_id': experiment_id,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member,
                      'cer': cer
                  })

