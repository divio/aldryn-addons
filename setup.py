# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_addons import __version__


setup(
    name='aldryn-addons',
    version=__version__,
    description='Aldryn Addons Framework',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-addons',
    packages=find_packages(),
    install_requires=(
        # 'Django',  # intentionally left out as a workaround for pips ignorance regarding exact versions to install
        'django-getenv',
    ),
    include_package_data=True,
    zip_safe=False,
)
