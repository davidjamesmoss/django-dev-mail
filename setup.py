#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-dev-mail',
    version='0.9',
    description='A simple django mail app for use in development.',
    author='David Moss',
    author_email='david@illansis.com',
    license='Python License',
    url='https://github.com/davidjamesmoss/django-dev-mail',
    packages=find_packages(),
    install_requires=[],
    package_data={
        '': [
            'templates/*/*.html',
        ],
    },
)
