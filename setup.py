from setuptools import find_packages, setup

from aldryn_addons import __version__


REQUIREMENTS = [
    "django",
    "django-getenv",
]


CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Framework :: Django",
    "Framework :: Django :: 3.2",
    "Framework :: Django :: 4.2",
    "Framework :: Django CMS",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
]


setup(
    name="aldryn-addons",
    version=__version__,
    author="Divio AG",
    author_email="info@divio.ch",
    url="https://github.com/divio/aldryn-addons",
    license="BSD-3-Clause",
    description="Aldryn Addons Framework",
    long_description=open("README.rst").read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite="tests.settings.run",
)
