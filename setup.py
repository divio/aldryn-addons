# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_addons import __version__

REQUIREMENTS = [
    # intentionally left out as a workaround for pips ignorance regarding
    # exact versions to install
    # 'Django',
    'django-getenv',
    'six',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-addons',
    version=__version__,
    description='Aldryn Addons Framework',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-addons',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)
