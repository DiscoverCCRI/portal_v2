from django.urls import path

from portal.apps.profiles.views import profile

urlpatterns = [
    path('', profile, name='profile'),
]
