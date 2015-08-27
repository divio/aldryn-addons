#######################
Aldryn Addons Framework
#######################


|PyPI Version|

`Aldryn addons`_ are re-usable django apps that follow certain conventions to
abstract out complicated configuration from the individual django website
project into upgradable packages. With this approach it is possible
to avoid repetitive "add this to ``INSTALLED_APPS`` and that to
``MIDDLEWARE_CLASSES`` and add these to ``urls.py``" work. The settings logic
is bundled with the Addon and only interesting "meta" settings are exposed.

``aldryn-addons`` is a framework to utilise such Addons in django projects.

The goal is to keep the footprint inside the django website project as small
as possible, so updating things usually just mean bumping a version in
``requirements.txt`` and no other changes in the project.


======================
Installation & Updates
======================

*********************
Aldryn Platform Users
*********************

Nothing to do. ``aldryn-addons`` is part of the Aldryn Platform.

*******************
Manual Installation
*******************

Add ``aldryn-addons`` to your projects ``requirements.txt`` or pip install it.
It is also highly recommended to install ``aldryn-django``. This is django
itself bundled as an Addon.
::

    pip install aldryn-addons aldryn-django==1.6.11


settings.py
===========

At the top if the settings the following code snippet::

    INSTALLED_ADDONS = [
        'aldryn-django',
    ]

    # add your own settings here that are needed by the installed Addons

    import aldryn_addons.settings
    aldryn_addons.settings.load(locals())

    # add any other custom settings here


urls.py
=======

Addons can automatically add stuff to the root ``urls.py`` so it's necessary
to add ``aldryn_addons.urls.patterns()`` and
``aldryn_addons.urls.i18n_patterns()``.
The code below is for Django 1.8 and above. For older versions of Django,
please add the prefix parameter to ``i18n_patterns``: ``i18n_patterns('', ...``
::

    from django.conf.urls import url, include
    from django.conf.urls.i18n import i18n_patterns
    import aldryn_addons.urls


    urlpatterns = [
        # add your own patterns here
    ] + aldryn_addons.urls.patterns() + i18n_patterns(
        # add your own i18n patterns here
        url(r'^myapp/', include('myapp.urls')),
        *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
    )


Please follow the installation instructions for aldryn-django for complete
integration.
Then follow the setup instructions for aldryn-cms for the examples below.


Adding Addons
=============

In this example we're going to install `Aldryn Newsblog`_, which requires
`django CMS`_.

pip install the Addon::

    pip install aldryn-newsblog

Add it to ``INSTALLED_ADDONS`` in ``settings.py``::

    INSTALLED_ADDONS = [
        'aldryn-django',
        'aldryn-cms',
        'aldryn-newsblog',
    ]

Copy ``aldryn_config.py`` and ``addon.json`` from the Addon into the ``addons``
directory within your project (``addons/aldryn-newsblog/aldryn_config.py`` and
``addons/aldryn-newsblog/addon.json``). If ``aldryn_config.py`` defines any
settings on the settings Form, put them in
``addons/aldryn-newsblog/settings.json``, if not put ``{}`` into it.

.. Note:: The need to manually copy ``aldryn_config.py`` and ``addon.json`` is
          due to legacy compatibility with the Aldryn Platform and will no
          longer be necessary in a later release.

.. Note:: Future versions will include a little webserver with a graphical UI
          to edit the settings in ``settings.json``, much like it is provided
          on the Aldryn Platform.


You are all set. The code in ``aldryn_config.py`` will take care of configuring
the Addon.


============
Contributing
============

This is a community project. We love to get any feedback in the form of
`issues`_ and `pull requests`_. Before submitting your pull request, please
review our guidelines for `Aldryn addons`_.

.. _issues: https://github.com/aldryn/aldryn-addons/issues
.. _pull requests: https://github.com/aldryn/aldryn-addons/pulls
.. _Aldryn addons: http://docs.aldryn.com/en/latest/reference/addons/index.html
.. _Aldryn Newsblog: https://github.com/aldryn/aldryn-newsblog
.. _django CMS: https://github.com/aldryn/aldryn-cms

.. |PyPI Version| image:: http://img.shields.io/pypi/v/aldryn-addons.svg
   :target: https://pypi.python.org/pypi/aldryn-addons
