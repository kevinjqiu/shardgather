# TODO: http://pypi.python.org/pypi?%3Aaction=list_classifiers
from setuptools import setup, find_packages


version = '0.1.2'


with open('requirements.txt') as f:
    dependencies = f.readlines()


setup(
    name='shardgather',
    version=version,
    description="A tool for running SQL on multiple sharded databases",
    long_description="",
    classifiers=[],
    keywords='cli',
    author='Kevin Jing Qiu',
    author_email='kevin@idempotent.ca',
    url='https://github.com/kevinjqiu/shardgather',
    license='Apache',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={
        'console_scripts': [
            "shardgather=shardgather.cli:main"
        ]
    }
)
