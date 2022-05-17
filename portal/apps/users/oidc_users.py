from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import unicodedata
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import update_last_login
from portal.apps.profiles.models import AerpawUserProfile
from uuid import uuid4


def get_tokens_for_user(user) -> None:
    profile = AerpawUserProfile.objects.get(pk=user.profile_id)
    refresh = RefreshToken.for_user(user)
    profile.refresh_token = str(refresh)
    profile.access_token = str(refresh.access_token)
    profile.modified_by = user.oidc_email
    profile.save()


def refresh_access_token_for_user(user):
    access = AccessToken.for_user(user)
    print(access)


def generate_username(email):
    # Using Python 3 and Django 1.11+, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    return unicodedata.normalize('NFKC', email)[:150]


class MyOIDCAB(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(MyOIDCAB, self).create_user(claims)
        user.created_by = claims.get('email', '')
        user.display_name = claims.get('given_name', '') + ' ' + claims.get('family_name', '')
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.modified_by = claims.get('email', '')
        user.oidc_email = claims.get('email', '')
        user.oidc_sub = claims.get('sub', '')
        user.profile = AerpawUserProfile.objects.create(
            created_by=claims.get('email', ''),
            modified_by=claims.get('email', ''),
            uuid=str(uuid4())
        )
        user.uuid = str(uuid4())
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        update_last_login(None, user)
        user.save()

        return user

