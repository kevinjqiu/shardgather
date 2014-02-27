from setuptools import setup, find_packages
import sys, os

version = '01'

setup(name='shardgather',
      version=version,
      description="A tool for running SQL on multiple sharded databases",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='cli',
      author='Kevin Jing Qiu',
      author_email='kevin.jing.qiu@gmail.com',
      url='',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
