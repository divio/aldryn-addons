# -*- coding: utf-8 -*-
import json
import os
import six
from getenv import env, ImproperlyConfigured
from django.conf import global_settings as _gs
global_settings = {key: value for key, value in _gs.__dict__.items() if key.upper() == key}


class NoDefault(object):
    pass


def boolean_ish(value):
    if isinstance(value, six.string_types):
        value = value.lower()
    if value in [True, 'true', '1', 'on', 'yes', 'y', 'yeah', 'yep']:
        return True
    elif value in [False, 'false', '0', 'off', 'no', 'n', 'nope']:
        return False
    return bool(value)


def json_from_file(path):
    try:
        with open(path) as fobj:
            return json.load(fobj)
    except ValueError as e:
        raise ValueError('{} ({})'.format(e, path))


def mkdirs(path):
    try:
        os.makedirs(path)
    except os.error:
        if not os.path.exists(path):
            raise


def openfile(path):
    """
    opens the file, creating it and directories if needed
    """
    mkdirs(os.path.dirname(path))
    return open(path, 'w+')


def senv(key, default=NoDefault, required=False, settings=None, _altered_defaults=None, _defaults=None):
    """
    return the value for key by checking the following sources:
        - the environment
        - the settings dictionary
    if the key is in _defaults but not in _altered_defaults, don't consider the value in settings
    """
    _altered_defaults = _altered_defaults or []
    _defaults = _defaults or []
    settings = settings or {}
    value = env(
        key,
        settings.get(key, default)
        if (key not in _defaults or (key in _defaults and key in _altered_defaults))
        else default,
    )
    if value == NoDefault:
        if required:
            raise ImproperlyConfigured((
                "Missing required setting '{}' "
                "(checked environment and settings)").format(key))
        else:
            value = None
    return value


def djsenv(key, *args, **kwargs):
    """
    like senv, but only uses the value for django default settings if they have
    actually been altered by the user in settings.py.
    """
    kwargs['_altered_defaults'] = getattr(kwargs.get('settings', {}), 'altered_keys', set())
    kwargs['_defaults'] = global_settings.keys()
    return senv(key, *args, **kwargs)


def remove_duplicates(seq):
    # list(set(seq)) does not work because it does not preserve order
    # http://stackoverflow.com/a/480227/245810
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
