from django.urls import path

from portal.apps.resources.views import resource_create, resource_detail, resource_edit, resource_list

urlpatterns = [
    path('', resource_list, name='resource_list'),
    path('create', resource_create, name='resource_create'),
    path('<int:resource_id>', resource_detail, name='resource_detail'),
    path('<int:resource_id>/edit', resource_edit, name='resource_edit'),
]
