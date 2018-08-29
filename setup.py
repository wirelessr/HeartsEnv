# setup.py
from os import environ
from setuptools import find_packages, setup


if __name__ == '__main__':
    setup(
        name='HeartsEnv',
        version='1.0',
        description='',
        long_description='',
        classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        keywords='',
        author='',
        author_email='',
        url='',
        license='',
        packages=find_packages(exclude=["ez_setup", "examples", "*.tests", "*.tests.*", "tests.*", "tests"]),
        include_package_data=True,
        zip_safe=False,
        install_requires=[],
        data_files=[],
        entry_points={
              'console_scripts': [
                  #'dm_verify_csv_files = digmine.console_master:verify_csv_files',
              ]
        }
    )