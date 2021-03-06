#!/usr/bin/env python

from setuptools import setup
setup(name='eeganalyse',
      version='0.1.1',
      description='A Simple, easily re-useable toolbox in python which will help researchers read, analyse and visualize EEG recorded and distributed in various formats.',
      author='Abhijith Mundanad Narayanan',
      author_email='mabhijithn@fastmail.com',
      packages=['eegbasic'],
      classifiers=[
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
      ],
      python_requires='>=3.6',
      install_requires=['numpy', 'scipy', 'resampy', 'pyEDFlib']
     )