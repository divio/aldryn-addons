# -*- coding: utf-8 -*-
from functools import partial
import imp
import os
import shutil
import uuid
from . import utils
from .utils import global_settings
from .exceptions import ImproperlyConfigured
from pprint import pformat
import six
from six.moves import UserDict


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
        if six.PY3:
            UserDict.update(self, *args, **kwargs)
        else:
            self._update_py2(*args, **kwargs)

    def _update_py2(*args, **kwargs):
        # copied from python2 standardlib UserDict.update() and altered a little
        # (see commented out lines below)
        if not args:
            raise TypeError("descriptor 'update' of 'UserDict' object "
                            "needs an argument")
        self = args[0]
        args = args[1:]
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            dict = args[0]
        elif 'dict' in kwargs:
            dict = kwargs.pop('dict')
            import warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          PendingDeprecationWarning, stacklevel=2)
        else:
            dict = None
        if dict is None:
            pass
        # elif isinstance(dict, UserDict):
        #     self.data.update(dict.data)
        # elif isinstance(dict, type({})) or not hasattr(dict, 'items'):
        elif not hasattr(dict, 'items'):
            # this case is not covered for altered state tracking
            self.data.update(dict)
        else:
            for k, v in dict.items():
                self[k] = v
        if len(kwargs):
            # self.data.update(kwargs)
            for k, v in kwargs.items():
                self[k] = v

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
            settings.update_without_tracking_altered_state(
                aldryn_config.Form().to_settings(addon_settings, settings),
            )
    # backwards compatibility for when installed-apps was defined in addon.json
    for app in addon_json.get('installed-apps', []):
        if app not in settings['INSTALLED_APPS']:
            settings['INSTALLED_APPS'].append(app)
    # remove duplicates
    settings['INSTALLED_APPS'] = utils.remove_duplicates(settings['INSTALLED_APPS'])
    settings['MIDDLEWARE_CLASSES'] = utils.remove_duplicates(settings['MIDDLEWARE_CLASSES'])
