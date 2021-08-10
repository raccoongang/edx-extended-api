#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import re

from setuptools import setup, find_packages


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


VERSION = get_version('edx_extended_api', '__init__.py')
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='edx-extended-api',
    version=VERSION,
    description="""Open-edx plugin with extended APIs""",
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ],
    zip_safe=False,
    keywords='edx extended api',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        "lms.djangoapp": [
            "edx_extended_api = edx_extended_api.apps:EdxExtendedApiConfig",
        ],
        "cms.djangoapp": [
        ],
    }
)
