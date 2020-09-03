import imp
import os
import shutil
import uuid
from collections import UserDict
from distutils.version import LooseVersion
from functools import partial
from pprint import pformat

from django import get_version

from . import utils
from .exceptions import ImproperlyConfigured
from .utils import global_settings


DJANGO_GTE_31 = LooseVersion(get_version()) >= LooseVersion("3.1")


def save_settings_dump(settings, path):
    to_dump = {key: value for key, value in settings.items() if key == key.upper()}
    with open(path, 'w+') as fobj:
        fobj.write(
            pformat(
                to_dump,
                indent=4,
            )
        )


def count_str(number):
    return '{0:05d}'.format(number)


class SettingsDictWrapper(UserDict):
    """
    hack to get around detecting if an altered setting was actually explicitly
    set or just happens to be the same as the django default.
    """
    def __init__(self, wrapped, watched_keys):
        self.data = wrapped
        self._watched_keys = watched_keys
        self.altered_keys = set()
        # register any already set settings as altered keys, if necessary
        for key, value in self.data.items():
            if key in self._watched_keys:
                self[key] = value

    def __setitem__(self, key, value):
        if key in self._watched_keys:
            self.altered_keys.add(key)
        self.set(key, value)

    def set(self, key, value):
        UserDict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        UserDict.update(self, *args, **kwargs)

    def update_without_tracking_altered_state(self, a_dict):
        for key, value in a_dict.items():
            self.set(key, value)


def load(settings, **kwargs):
    global_debug = utils.boolean_ish(os.environ.get('ALDRYN_ADDONS_DEBUG', False))
    # fallback to global debug flag
    debug = kwargs.get('debug', global_debug)

    settings = SettingsDictWrapper(
        settings,
        watched_keys=global_settings.keys(),
    )
    env = partial(utils.djsenv, settings=settings)
    settings['BASE_DIR'] = env(
        'BASE_DIR',
        os.path.dirname(os.path.abspath(settings['__file__']))
    )

    settings['ADDONS_DIR'] = env(
        'ADDONS_DIR',
        os.path.join(settings['BASE_DIR'], 'addons')
    )
    settings['ADDONS_DEV_DIR'] = env(
        'ADDONS_DEV_DIR',
        os.path.join(settings['BASE_DIR'], 'addons-dev')
    )
    utils.mkdirs(settings['ADDONS_DEV_DIR'])
    utils.mkdirs(settings['ADDONS_DIR'])

    if debug:
        # TODO: .debug is not multi-process safe!
        debug_path = os.path.join(settings['ADDONS_DIR'], '.debug')
        shutil.rmtree(debug_path, ignore_errors=True)
        utils.mkdirs(debug_path)

    def dump(obj, count, name):
        if not debug:
            # do nothing if debug is not turned on
            return 0
        dump_name = '{}-{}.dump'.format(count_str(count), name)
        dump_path = os.path.join(debug_path, dump_name)
        save_settings_dump(obj, dump_path)
        return count + 1

    debug_count = 0
    debug_count = dump(settings, debug_count, 'initial')

    # load global defaults
    for key, value in global_settings.items():
        if key not in settings:
            # SettingsDictWrapper.set skips the default settings change
            # recording
            settings.set(key, value)

    debug_count = dump(settings, debug_count, 'load-globals')

    # normalise tuple settings to lists
    for key, value in settings.items():
        if isinstance(value, tuple):
            settings.set(key, list(value))

    debug_count = dump(settings, debug_count, 'normalise')

    # add Addon default settings if they are not there yet
    settings.setdefault('ADDON_URLS', [])
    settings.setdefault('ADDON_URLS_I18N', [])
    settings.setdefault('INSTALLED_APPS', [])
    settings['INSTALLED_APPS'].append('aldryn_addons')
    # load Addon settings
    if not (settings['INSTALLED_ADDONS'] and settings['ADDONS_DIR']):
        return
    for addon_name in settings['INSTALLED_ADDONS']:
        if os.path.isabs(addon_name):
            addon_path = addon_name
            addon_name = os.path.basename(os.path.normpath(addon_path))
            settings_json_path = None
        else:
            addon_dev_path = os.path.join(settings['ADDONS_DEV_DIR'], addon_name)
            addon_normal_path = os.path.join(settings['ADDONS_DIR'], addon_name)
            settings_json_path = os.path.join(addon_normal_path, 'settings.json')
            if os.path.exists(addon_dev_path):
                addon_path = addon_dev_path
            elif os.path.exists(addon_normal_path):
                addon_path = addon_normal_path
            else:
                raise ImproperlyConfigured(
                    '{} Addon not found (tried {} and {})'.format(
                        addon_name, addon_dev_path, addon_normal_path,
                    )
                )
        load_addon_settings(
            name=addon_name,
            path=addon_path,
            settings=settings,
            settings_json_path=settings_json_path,
        )
        debug_count = dump(settings, debug_count, addon_name)
    # The Divio Cloud settings system through Aldryn Addons overrides the
    # default Django settings triggering an error in Django >= 3.1:
    # https://github.com/django/django/blob/d907371ef99a1e4ca6bc1660f57d81f265750984/django/conf/__init__.py#L195-L202
    # To remedy this, we need to delete the settings when they are not
    # overridden by the user (using the Django defaults)
    if DJANGO_GTE_31:
        if settings.get('PASSWORD_RESET_TIMEOUT') == 60 * 60 * 24 * 3:
            del settings["PASSWORD_RESET_TIMEOUT"]
        if settings.get('PASSWORD_RESET_TIMEOUT_DAYS') == 3:
            del settings["PASSWORD_RESET_TIMEOUT_DAYS"]


def load_addon_settings(name, path, settings, **kwargs):
    addon_json_path = kwargs.get('addon_json_path', os.path.join(path, 'addon.json'))
    addon_json = utils.json_from_file(addon_json_path)
    settings_json_path = kwargs.get('settings_json_path', os.path.join(path, 'settings.json'))
    # TODO: once we have optional "secrets" support on fields:
    #       load the secret settings from environment variables here and add
    #       them to addon_settings
    aldryn_config_py_path = kwargs.get('aldryn_config_py_path', os.path.join(path, 'aldryn_config.py'))
    if os.path.exists(aldryn_config_py_path):
        aldryn_config = imp.load_source(
            '{}_{}'.format(name, uuid.uuid4()).replace('-', '_'),
            aldryn_config_py_path,
        )
        # Usually .to_settings() implementations will update settings in-place, as
        # well as returning the resulting dict.
        # But because the API is not defined clear enough, some might return a new
        # dict with just their generated settings. So we also update the settings
        # dict here, just to be sure.
        if hasattr(aldryn_config, 'Form'):
            try:
                addon_settings = utils.json_from_file(settings_json_path)
            except (ValueError, OSError):
                try:
                    addon_settings = utils.json_from_file(os.path.join(path, 'settings.json'))
                except (ValueError, OSError):
                    addon_settings = {}

            # fill up remaining fields in
            # addon_settings with defaults
            form = aldryn_config.Form()
            for field_name, field in form._fields:
                if field_name not in addon_settings:
                    addon_settings[field_name] = field.initial

            settings.update_without_tracking_altered_state(
                aldryn_config.Form().to_settings(addon_settings, settings),
            )
    # backwards compatibility for when installed-apps was defined in addon.json
    for app in addon_json.get('installed-apps', []):
        if app not in settings['INSTALLED_APPS']:
            settings['INSTALLED_APPS'].append(app)
    # remove duplicates
    settings['INSTALLED_APPS'] = utils.remove_duplicates(settings['INSTALLED_APPS'])

    if settings.get('MIDDLEWARE_CLASSES') is not None:
        # Django<2
        settings['MIDDLEWARE_CLASSES'] = utils.remove_duplicates(settings['MIDDLEWARE_CLASSES'])

    if settings.get('MIDDLEWARE') is not None:
        # Django>=1.11
        settings['MIDDLEWARE'] = utils.remove_duplicates(settings['MIDDLEWARE'])
