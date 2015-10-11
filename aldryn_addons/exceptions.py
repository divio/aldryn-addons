# -*- coding: utf-8 -*-


class ImproperlyConfigured(Exception):
    """
    We do not use django.core.exceptions.ImproperlyConfigured, because
    manage.py will actually silently swallow those, thus not showing us the
    real error.
    https://github.com/django/django/blob/1.6.11/django/core/management/__init__.py#L108
    this is still true up until at least Django 1.9:
    https://github.com/django/django/blob/3f22e83e90bc2eeea5f65858660385a34fbf5486/django/core/management/__init__.py#L299
    """
    pass
