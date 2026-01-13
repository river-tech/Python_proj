from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def is_admin(user):
    return getattr(user, "role", None) == "ADMIN"


def is_teacher(user):
    return getattr(user, "role", None) == "TEACHER"


def is_student(user):
    return getattr(user, "role", None) == "STUDENT"


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            if getattr(request.user, "role", None) not in roles:
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
