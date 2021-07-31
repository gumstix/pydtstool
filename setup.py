##################################################
#                    pyDtsTool                   #
#           Copyright 2021, Altium, Inc.         #
#  Author: Keith Lee                             #
#  E-Mail: keith.lee@altium.com                  #
##################################################

from setuptools import setup, find_packages

setup(name='pyDtsTool',
      version='0.1',
      license='GPLv3',
      author_email='keith.lee@altium.com',
      description='Manipulate device trees as abstract data type',
      packages=find_packages(exclude=['tests', 'debug_lib']),
      install_requires=open('requirements.txt').read(),
      long_description=open('README.md').read(),
      zip_safe=False,
      python_requires='>-3.6',)
