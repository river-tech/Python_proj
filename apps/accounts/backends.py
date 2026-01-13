from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db.models import Q

from apps.accounts.models import User


class AccountUserBackend(BaseBackend):
    """
    Authenticate against accounts_user table (managed=False).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(Q(username=username))
        except User.DoesNotExist:
            return None

        if user.is_active and check_password(password, user.password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
