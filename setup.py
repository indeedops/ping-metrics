#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cross-dc-metrics',
    version='1.4',
    description='Emit cross datacenter metrics to Data Dog or statsd',
    long_description=long_description,
    author='Said Babayev',
    author_email='said@indeed.com',
    url='https://github.com/indeedops/ping-metrics',
    packages=['cross_dc_metrics'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cross_dc_metrics=cross_dc_metrics.__main__:main',
        ],
    },
    data_files=[
        ('/etc/cross_dc_metrics', ['config.ini']),
    ],
)
