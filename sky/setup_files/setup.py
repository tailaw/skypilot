"""SkyPilot.

SkyPilot is a framework for easily running machine learning* workloads on any
cloud through a unified interface. No knowledge of cloud offerings is required
or expected – you simply define the workload and its resource requirements, and
SkyPilot will automatically execute it on AWS, Google Cloud Platform or
Microsoft Azure.

*: SkyPilot is primarily targeted at machine learning workloads, but it can
also support many general workloads. We're excited to hear about your use case
and would love to hear more about how we can better support your requirements -
please join us in [this
discussion](https://github.com/skypilot-org/skypilot/discussions/1016)
"""

import io
import os
import platform
import re
import warnings
from typing import Dict, List

import setuptools

ROOT_DIR = os.path.dirname(__file__)

system = platform.system()
if system == 'Darwin':
    mac_version = platform.mac_ver()[0]
    mac_major, mac_minor = mac_version.split('.')[:2]
    mac_major = int(mac_major)
    mac_minor = int(mac_minor)
    if mac_major < 10 or (mac_major == 10 and mac_minor < 15):
        warnings.warn(
            f'\'Detected MacOS version {mac_version}. MacOS version >=10.15 '
            'is required to install ray>=1.9\'')


def find_version(*filepath):
    # Extract version information from filepath
    # Adapted from:
    #  https://github.com/ray-project/ray/blob/master/python/setup.py
    with open(os.path.join(ROOT_DIR, *filepath)) as fp:
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                                  fp.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError('Unable to find version string.')


def parse_readme(readme: str) -> str:
    """Parse the README.md file to be pypi compatible."""
    # Replace the footnotes.
    readme = readme.replace('<!-- Footnote -->', '#')
    footnote_re = re.compile(r'\[\^([0-9]+)\]')
    readme = footnote_re.sub(r'<sup>[\1]</sup>', readme)

    # Remove the dark mode switcher
    mode_re = re.compile(
        r'<picture>[\n ]*<source media=.*>[\n ]*<img(.*)>[\n ]*</picture>',
        re.MULTILINE)
    readme = mode_re.sub(r'<img\1>', readme)
    return readme


install_requires = [
    'wheel',
    # NOTE: ray 2.0.1 requires click<=8.0.4,>=7.0; We disable the
    # shell completion for click<8.0 for backward compatibility.
    'click<=8.0.4,>=7.0',
    # NOTE: required by awscli. To avoid ray automatically installing
    # the latest version.
    'colorama<0.4.5',
    'cryptography',
    # Jinja has a bug in older versions because of the lack of pinning
    # the version of the underlying markupsafe package. See:
    # https://github.com/pallets/jinja/issues/1585
    'jinja2>=3.0',
    'jsonschema',
    'networkx',
    'oauth2client',
    'pandas',
    'pendulum',
    # PrettyTable with version >=2.0.0 is required for the support of
    # `add_rows` method.
    'PrettyTable>=2.0.0',
    # Lower local ray version is not fully supported, due to the
    # autoscaler issues (also tracked in #537).
    'ray[default]>=1.9.0,<=2.3.0',
    'rich',
    'tabulate',
    'typing-extensions',
    'filelock',  # TODO(mraheja): Enforce >=3.6.0 when python version is >= 3.7
    # This is used by ray. The latest 1.44.0 will generate an error
    # `Fork support is only compatible with the epoll1 and poll
    # polling strategies`
    'grpcio>=1.32.0,<=1.43.0',
    'packaging',
    # The latest 4.21.1 will break ray. Enforce < 4.0.0 until Ray releases the
    # fix.
    # https://github.com/ray-project/ray/pull/25211
    'protobuf<4.0.0',
    'psutil',
    'pulp',
]

# NOTE: Change the templates/spot-controller.yaml.j2 file if any of the following
# packages dependencies are changed.
aws_dependencies = [
    # awscli>=1.27.10 is required for SSO support.
    'awscli',
    'boto3',
    # 'Crypto' module used in authentication.py for AWS.
    'pycryptodome==3.12.0',
]
extras_require: Dict[str, List[str]] = {
    'aws': aws_dependencies,
    # TODO(zongheng): azure-cli is huge and takes a long time to install.
    # Tracked in: https://github.com/Azure/azure-cli/issues/7387
    # azure-identity is needed in node_provider.
    'azure': [
        'azure-cli>=2.31.0', 'azure-core', 'azure-identity',
        'azure-mgmt-network'
    ],
    'gcp': ['google-api-python-client', 'google-cloud-storage'],
    'docker': ['docker'],
    'lambda': [],
    'cloudflare': aws_dependencies
}

extras_require['all'] = sum(extras_require.values(), [])

# Install aws requirements by default, as it is the most common cloud provider,
# and the installation is quick.
install_requires += extras_require['aws']

long_description = ''
readme_filepath = 'README.md'
# When sky/backends/wheel_utils.py builds wheels, it will not contain the
# README.  Skip the description for that case.
if os.path.exists(readme_filepath):
    long_description = io.open(readme_filepath, 'r', encoding='utf-8').read()
    long_description = parse_readme(long_description)

setuptools.setup(
    # NOTE: this affects the package.whl wheel name. When changing this (if
    # ever), you must grep for '.whl' and change all corresponding wheel paths
    # (templates/*.j2 and wheel_utils.py).
    name='skypilot',
    version=find_version('sky', '__init__.py'),
    packages=setuptools.find_packages(),
    author='SkyPilot Team',
    license='Apache 2.0',
    readme='README.md',
    description='SkyPilot: An intercloud broker for the clouds',
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['wheel'],
    requires_python='>=3.6',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['sky = sky.cli:cli'],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ],
    project_urls={
        'Homepage': 'https://github.com/skypilot-org/skypilot',
        'Issues': 'https://github.com/skypilot-org/skypilot/issues',
        'Discussion': 'https://github.com/skypilot-org/skypilot/discussions',
        'Documentation': 'https://skypilot.readthedocs.io/en/latest/',
    },
)
