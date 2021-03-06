#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""undiscord setup.py"""

import codecs
import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


def find_version(*file_paths):
    with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *file_paths), "r") as fp:
        version_file = fp.read()
    m = re.search(r"^__version__ = \((\d+), ?(\d+), ?(\d+)\)", version_file, re.M)
    if m:
        return "{}.{}.{}".format(*m.groups())
    raise RuntimeError("Unable to find a valid version")


VERSION = find_version("undiscord", "__init__.py")


class Pylint(test):
    user_options = [('pylint-args=', 'a', "Arguments to pass to pylint")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pylint_args = "undiscord --persistent=y --rcfile=.pylintrc --output-format=colorized"

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        from pylint.lint import Run
        Run(shlex.split(self.pylint_args))


class PyTest(test):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = "-v --cov={}".format("undiscord")

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def readme():
    with open("README.rst", encoding="utf-8") as f:
        return f.read()


setup(
    name="undiscord",
    version=VERSION,
    description="A Discord Bot for 2019 Level Up Hackathon",
    long_description=readme(),
    author="Nathan Klapstein, Ryan Furrer",
    author_email="nklapste@ualberta.ca",
    url="https://github.com/nklapste/undiscord",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=[
        "discord.py",
        "plotly>=3.5.0,<4.0.0",
        "pendulum>=2.0.4,<3.0.0",
        "flask-restplus>=0.12.1,<1.0.0",
        "cheroot>=6.5.4,<7.0.0",
        "flask>=1.0.2,<2.0.0",
        "networkx>=2.2",
        "matplotlib>=3.0.2,<4.0.0",
        "numpy>=1.15.4,<2.0.0",
    ],
    tests_require=[
        "pytest>=4.1.0,<5.0.0",
        "pytest-cov>=2.6.1,<3.0.0",
        "pylint>=2.2.2,<3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "undiscord-bot = undiscord.bot.__main__:main",
            "undiscord-server = undiscord.server.__main__:main",
        ],
    },
    cmdclass={"test": PyTest, "lint": Pylint},
)
