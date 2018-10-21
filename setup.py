#!/usr/bin/env python
from setuptools import setup

requires = []

try:
    import argparse
except ImportError:
    requires.append('argparse')

entry_points = {
    'console_scripts': [
        'rcs-latexdiff = rcs_latexdiff.rcs_latexdiff:main',
   ]
}

setup(
    name = "rcs-latexdiff",
    version = "1.0",
    url = 'https://github.com/driquet/rcs-latexdiff',
    author = 'Damien Riquet',
    author_email = 'd.riquet@gmail.com',
    description = "A tool to compare a LaTeX file for two rcs commits.",
    long_description=open('README.rst').read(),
    packages = ['rcs_latexdiff'],
    include_package_data = True,
    install_requires = requires,
    entry_points = entry_points,
    test_suite = "test"
)
