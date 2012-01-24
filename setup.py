#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='reddit_about',
    description='reddit about pages',
    version='0.1',
    author='Max Goodman',
    author_email='max@reddit.com',
    packages=find_packages(),
    install_requires=[
        'r2',
    ],
    extras_require={
        'stats': ['google-api-python-client'],
    },
    entry_points={
        'r2.plugin':
            ['about = reddit_about:About']
    },
    include_package_data=True,
    zip_safe=False,
)
