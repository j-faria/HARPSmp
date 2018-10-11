#!/usr/bin/env python

from setuptools import setup

setup(name='HARPSmp',
      version='0.1',
      description='A helper package for the HARPS metal-poor sample',
    #   long_description=open('README.rst').read(),
      author='João Faria',
      author_email='joao.faria@astro.up.pt',
      license='GPL-3.0',
      url='https://github.com/j-faria/harpsmp',
      packages=['harpsmp'],
      classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
      ),
     )