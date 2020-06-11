#!/usr/bin/env python

import os
import shutil
import sys
import json

from setuptools import setup, find_packages

import pyct.build

def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except Exception:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, "
              "this warning can safely be ignored. If you are creating a package or "
              "otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']


def _build_paneljs():
    from bokeh.ext import build
    print("Building custom models:")
    panel_dir = os.path.join(os.path.dirname(__file__), "panel")
    build(panel_dir)


class CustomDevelopCommand(develop):
    """Custom installation for development mode."""

    def run(self):
        _build_paneljs()
        develop.run(self)


class CustomInstallCommand(install):
    """Custom installation for install mode."""

    def run(self):
        _build_paneljs()
        install.run(self)


class CustomSdistCommand(sdist):
    """Custom installation for sdist mode."""

    def run(self):
        _build_paneljs()
        sdist.run(self)


_COMMANDS = {
    'develop': CustomDevelopCommand,
    'install': CustomInstallCommand,
    'sdist':   CustomSdistCommand,
}

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheelCommand(bdist_wheel):
        """Custom bdist_wheel command to force cancelling qiskit-terra wheel
        creation."""

        def run(self):
            """Do nothing so the command intentionally fails."""
            _build_paneljs()
            bdist_wheel.run(self)

    _COMMANDS['bdist_wheel'] = CustomBdistWheelCommand
except Exception:
    pass

########## dependencies ##########

install_requires = [
    'param >=1.9.3,<2.0',
    'numpy >=1.0',
    'pyviz_comms >=0.7.3',
    'panel >=0.8.0',
    'pandas'
]

extras_require = {}

# Notebook dependencies
extras_require['notebook'] = [
    'ipython >=5.4.0',
    'notebook'
]

# IPython Notebook + pandas + matplotlib + bokeh
extras_require['recommended'] = extras_require['notebook'] + [
    'matplotlib >=2.2',
    'bokeh >=1.1.0'
]

# Requirements to run all examples
extras_require['examples'] = extras_require['recommended'] + [
    'networkx',
    'pillow',
    'xarray >=0.10.4',
    'plotly >=4.0',
    'streamz >=0.5.0',
    'datashader',
    'selenium',
    'phantomjs',
    'ffmpeg',
    'cftime',
    'netcdf4',
    'bzip2',
    'dask',
    'scipy',
    'shapely',
    'scikit-image'
]

if sys.version_info.major > 2:
    extras_require['examples'].append('spatialpandas')

# Extra third-party libraries
extras_require['extras'] = extras_require['examples']+[
    'cyordereddict',
    'pscript ==0.7.1'
]

# Test requirements
extras_require['tests'] = [
    'nose',
    'mock',
    'flake8 ==3.6.0',
    'coveralls',
    'path.py', 
    'matplotlib >=2.2,<3.1',
    'nbsmoke >=0.2.0',
    'pytest-cov ==2.5.1'
]

extras_require['unit_tests'] = extras_require['examples']+extras_require['tests']

extras_require['basic_tests'] = extras_require['tests']+[
    'matplotlib >=2.1',
    'bokeh >=1.1.0',
    'pandas'
] + extras_require['notebook']

extras_require['nbtests'] = extras_require['recommended'] + [
    'nose',
    'awscli',
    'deepdiff',
    'nbconvert ==5.3.1',
    'jsonschema ==2.6.0',
    'cyordereddict',
    'ipython ==5.4.1'
]

extras_require['doc'] = extras_require['examples'] + [
    'nbsite >0.5.2',
    'sphinx',
    'sphinx_holoviz_theme',
    'mpl_sample_data >=3.2.1',
    'awscli',
    'pscript',
    'graphviz'
]

extras_require['build'] = [
    'param >=1.7.0',
    'setuptools >=30.3.0',
    'pyct >=0.4.4',
    'python <3.8'
]

# Everything including cyordereddict (optimization) and nosetests
extras_require['all'] = list(set(extras_require['unit_tests']) | set(extras_require['nbtests']))

setup_args = dict(
    name='panel',
    version=get_setup_version("panel"),
    description='A high level app and dashboarding solution for Python.',
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    long_description_content_type="text/markdown",
    author="HoloViz",
    author_email="developers@holoviz.org",
    maintainer="HoloViz",
    maintainer_email="developers@holoviz.org",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='http://panel.holoviz.org',
    cmdclass=_COMMANDS,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'panel = panel.cli:main'
        ]},
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests']
)

if __name__ == "__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'panel', 'examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
