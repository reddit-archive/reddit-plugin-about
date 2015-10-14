#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='reddit_skeleton',
    description='reddit skeleton plugin based on about plugin: https://github.com/reddit/reddit-plugin-about',
    version='0.1',
    author='James Jones',
    author_email='james.voip+reddit-dev@gmail.com',
    packages=find_packages(),
    install_requires=[
        'r2',
    ],
    extras_require={
    },
    entry_points={
        'r2.plugin':
            ['skeleton = reddit_skeleton:Skeleton']
    },
    include_package_data=True,
    zip_safe=False,
)
