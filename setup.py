from setuptools import setup, find_packages

setup(
    name = 'pygalileo',
    version = '0.1',
    description = 'Simple script to generate a detector constellation with the Galileo spacecrafts',
    packages = find_packages(),
    package_data = {'': ['data/sat_data.mat']},
    include_package_data=True,
    long_description=open('README.txt').read()
)
