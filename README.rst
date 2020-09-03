=======================
Aldryn Addons Framework
=======================

|pypi| |build| |coverage|

**Aldryn Addons** are re-usable django apps that follow certain conventions to
abstract out complicated configuration from the individual django website
project into upgradable packages. With this approach it is possible
to avoid repetitive "add this to ``INSTALLED_APPS`` and that to
``MIDDLEWARE_CLASSES`` and add these to ``urls.py``" work. The settings logic
is bundled with the addon and only interesting "meta" settings are exposed.
It is a framework to utilise such addons in django projects.

The goal is to keep the footprint inside the django website project as small
as possible, so updating things usually just mean bumping a version in
``requirements.txt`` and no other changes in the project.

This addon still uses the legacy "Aldryn" naming. You can read more about this in our
`support section <https://support.divio.com/general/faq/essential-knowledge-what-is-aldryn>`_.


Contributing
============

This is a an open-source project. We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

We're grateful to all contributors who have helped create and maintain this package.
Contributors are listed at the `contributors <https://github.com/divio/aldryn-addons/graphs/contributors>`_
section.


Documentation
=============

See ``REQUIREMENTS`` in the `setup.py <https://github.com/divio/aldryn-addons/blob/master/setup.py>`_
file for additional dependencies:

|python| |django|


Installation
------------

``aldryn-addons`` is part of the Divio Cloud platform.

For a manual install:

Add ``aldryn-addons`` to your projects ``requirements.txt`` or pip install it.
It is also highly recommended to install ``aldryn-django``. This is django
itself bundled as an addon::

    pip install aldryn-addons aldryn-django==1.6.11

At the top if the ``settings.py`` add the following code snippet::

    INSTALLED_ADDONS = [
        'aldryn-django',
    ]

    # add your own settings here that are needed by the installed Addons

    import aldryn_addons.settings
    aldryn_addons.settings.load(locals())

    # add any other custom settings here

Addons can automatically add code to the root ``urls.py`` so it's necessary
to add ``aldryn_addons.urls.patterns()`` and
``aldryn_addons.urls.i18n_patterns()``.
The code below is for Django 1.8 and above. For older versions of Django,
please add the prefix parameter to ``i18n_patterns``: ``i18n_patterns('', ...``
::

    from django.urls import re_path, include
    from django.conf.urls.i18n import i18n_patterns
    import aldryn_addons.urls


    urlpatterns = [
        # add your own patterns here
    ] + aldryn_addons.urls.patterns() + i18n_patterns(
        # add your own i18n patterns here
        re_path(r'^myapp/', include('myapp.urls')),
        *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
    )


Please follow the installation instructions for aldryn-django for complete
integration. Then follow the setup instructions for aldryn-django-cms
for the examples below.


Adding Addons
-------------

In this example we're going to install `django CMS Link <https://github.com/divio/djangocms-link/>`_,
which requires `Aldryn django CMS <https://github.com/aldryn/aldryn-django-cms/>`_.

pip install the Addon::

    pip install djangocms-link

Add it to ``INSTALLED_ADDONS`` in ``settings.py``::

    INSTALLED_ADDONS = [
        'aldryn-django',
        'aldryn-cms',
        'djangocms-link',
    ]

Copy ``aldryn_config.py`` and ``addon.json`` from the addon into the ``addons``
directory within your project (``addons/djangocms-link/aldryn_config.py`` and
``addons/djangocms-link/addon.json``). If ``aldryn_config.py`` defines any
settings on the settings Form, put them in
``addons/djangocms-link/settings.json``, if not put ``{}`` into it.

.. Note:: The need to manually copy ``aldryn_config.py`` and ``addon.json`` is
          due to legacy compatibility with the Divio Cloud platform and will no
          longer be necessary in a later release.

.. Note:: Future versions will include a little webserver with a graphical UI
          to edit the settings in ``settings.json``, much like it is provided
          on the Divio Cloud platform.


You are all set. The code in ``aldryn_config.py`` will take care of configuring
the addon.


Running Tests
-------------

You can run tests by executing::

    virtualenv env
    source env/bin/activate
    pip install -r tests/requirements.txt
    python setup.py test


.. |pypi| image:: https://badge.fury.io/py/aldryn-addons.svg
    :target: http://badge.fury.io/py/aldryn-addons
.. |build| image:: https://travis-ci.org/divio/aldryn-addons.svg?branch=master
    :target: https://travis-ci.org/divio/aldryn-addons
.. |coverage| image:: https://codecov.io/gh/divio/aldryn-addons/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/divio/aldryn-addons

.. |python| image:: https://img.shields.io/badge/python-3.5+-blue.svg
    :target: https://pypi.org/project/aldryn-addons/
.. |django| image:: https://img.shields.io/badge/django-2.2,%203.0,%203.1-blue.svg
    :target: https://www.djangoproject.com/
