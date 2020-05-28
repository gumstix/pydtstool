from setuptools import setup, find_packages

setup(name='PyDeviceTree',
      version='0.1',
      license='GPLv3',
      author_email='keith.lee@gumstix.com',
      description='Manipulate device trees as abstract data type',
      packages=find_packages(exclude=['unittest']),
      long_description=open('README.md').read(),
      zip_safe=False)
