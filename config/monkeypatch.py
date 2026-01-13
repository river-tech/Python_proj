"""
Temporary compatibility patches for Django running on Python 3.14.

Context.__copy__ in Django 4.2 calls copy(super()) which breaks on Python 3.14.
This patch rewrites BaseContext.__copy__ to create a new instance explicitly.
"""
from copy import copy

from django.template import context as django_context


def _base_context_copy(self):
    duplicate = django_context.BaseContext.__new__(django_context.BaseContext)
    duplicate.dicts = list(self.dicts)
    return duplicate


# Apply patch once.
if getattr(django_context.BaseContext.__copy__, "__name__", "") != "_base_context_copy":
    django_context.BaseContext.__copy__ = _base_context_copy
