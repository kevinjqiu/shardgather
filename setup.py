#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


from shardgather import __version__
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
requirements = map(str.strip, open('requirements.txt').readlines())

setup(
    name='shardgather',
    version=__version__,
    description='A tool for executing SQL queries against sharded databases',
    long_description=readme + '\n\n' + history,
    author='Kevin Jing Qiu',
    author_email='kevin@idempotent.ca',
    url='https://github.com/kevinjqiu/shardgather',
    packages=[
        'shardgather',
    ],
    package_dir={'shardgather': 'shardgather'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='shardgather',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'shardgather=shardgather.cli:main'
        ]
    },
)
