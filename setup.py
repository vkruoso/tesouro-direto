from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys

import tesouro


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


curdir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(curdir, 'README.rst')) as readme:
    long_description = readme.read()

setup(
    # Basic info
    name='tesouro-direto',
    version=tesouro.__version__,
    url='http://github.com/vkruoso/tesouro-direto',
    license='MIT License',
    author='Vinicius K. Ruoso',
    author_email='vinicius.ruoso@gmail.com',
    description="Tools to manage 'Tesouro Direto' information.",
    long_description=long_description,

    # Details
    packages=['tesouro', 'tesouro.direto'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'requests',
        'jinja2'
    ],

    # Testing
    tests_require=['tox'],
    cmdclass={'test': Tox},

    # Scripts
    entry_points={
    },

    # Information
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
