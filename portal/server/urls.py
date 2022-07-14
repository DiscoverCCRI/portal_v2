"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from portal.apps.experiments.api.viewsets import CanonicalExperimentResourceViewSet, ExperimentSessionViewSet, \
    ExperimentViewSet, UserExperimentViewSet
from portal.apps.operations.api.viewsets import CanonicalNumberViewSet
from portal.apps.projects.api.viewsets import ProjectViewSet, UserProjectViewSet
from portal.apps.resources.api.viewsets import ResourceViewSet
from portal.apps.users.api.viewsets import UserViewSet

# Routers provide an easy way of automatically determining the URL conf.
# Ordering is important for overloaded API slugs with differing ViewSet definitions
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'canonical-experiment-number', CanonicalNumberViewSet, basename='canonical-experiment-number')
router.register(r'canonical-experiment-resource', CanonicalExperimentResourceViewSet,
                basename='canonical-experiment-resource')
router.register(r'experiments', ExperimentViewSet, basename='experiments')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'resources', ResourceViewSet, basename='resources')
router.register(r'sessions', ExperimentSessionViewSet, basename='sessions')
router.register(r'user-experiment', UserExperimentViewSet, basename='user-experiment')
router.register(r'user-project', UserProjectViewSet, basename='user-project')
router.register(r'users', UserViewSet, basename='users')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/', include('django.contrib.auth.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('profile/', include('portal.apps.profiles.urls')),  # profiles app
    path('resources/', include('portal.apps.resources.urls')),  # resources app
]
