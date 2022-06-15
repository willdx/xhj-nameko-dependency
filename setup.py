from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

version = '0.0.1'

install_requires = [
    "nameko",
    "pycryptodome",
    "requests"
]

setup(
    name='xhj-nameko-dependency',
    version=version,
    description="xhj nameko dependency",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='xhj nameko',
    author='william.dai',
    author_email='daixiang1992@gmail.com',
    url='',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
    }
)
