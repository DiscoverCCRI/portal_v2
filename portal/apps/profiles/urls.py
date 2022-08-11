from django.urls import path

from portal.apps.profiles.views import profile, credential

urlpatterns = [
    path('', profile, name='profile'),
    path('credentials/', credential, name='credential')
]
