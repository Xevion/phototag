"""
setup.py

The installation script responsible for setting up the CLI program on the user's system.
"""

import os
import sys

from setuptools import find_packages, setup

EXCLUDE_FROM_PACKAGES = []
CURDIR = sys.path[0]

with open(os.path.join(CURDIR, "README.md")) as file:
    README = file.read()

setup(
    name="phototag",
    version="0.1.0",
    author="Xevion",
    author_email="xevion@xevion.dev",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/xevion/phototag",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    keywords=[],
    scripts=[],
    entry_points="""
        [console_scripts]
        phototag=phototag.__main__:main
    """,
    zip_safe=False,
    python_requires=">=3.7",
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cachetools==5.3.0; python_version ~= '3.7'",
        "certifi==2023.5.7; python_version >= '3.6'",
        "charset-normalizer==3.1.0; python_full_version >= '3.7.0'",
        "click==7.1.2",
        "colorama==0.4.6; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6'",
        "colored-traceback==0.3.0",
        "commonmark==0.9.1",
        "google-api-core==2.11.0; python_version >= '3.7'",
        "google-api-python-client==2.86.0",
        "google-auth==2.18.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "google-auth-httplib2==0.1.0",
        "google-cloud-vision==3.4.1",
        "googleapis-common-protos==1.59.0; python_version >= '3.7'",
        "grpcio==1.54.0",
        "grpcio-status==1.54.0",
        "httplib2==0.22.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "idna==3.4; python_version >= '3.5'",
        "imagehash==4.1.0",
        "imageio==2.6.1",
        "iptcinfo3==2.1.4",
        "numpy==1.24.3; python_version >= '3.8'",
        "pillow==9.5.0",
        "proto-plus==1.22.2; python_version >= '3.6'",
        "protobuf==4.23.0",
        "pyasn1==0.5.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "pyasn1-modules==0.3.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "pygments==2.15.1; python_version >= '3.7'",
        "pyparsing==3.0.9; python_version >= '3.1'",
        "pywavelets==1.4.1; python_version >= '3.8'",
        "rawpy==0.18.1",
        "requests==2.30.0; python_version >= '3.7'",
        "rich==8.0.0",
        "rsa==4.9; python_version >= '3.6'",
        "scipy==1.10.1; python_version < '3.12' and python_version >= '3.8'",
        "setuptools==67.7.2",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "typing-extensions==3.10.0.2",
        "uritemplate==4.1.1; python_version >= '3.6'",
        "urllib3==1.26.15; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
    ],
    extras_require={
        "dev": [
            "appdirs==1.4.4",
            "attrs==23.1.0; python_version >= '3.7'",
            "black==19.10b0; python_version >= '3.6'",
            "cached-property==1.5.2",
            "cerberus==1.3.4",
            "certifi==2023.5.7; python_version >= '3.6'",
            "chardet==5.0.0; python_version >= '3.6'",
            "charset-normalizer==3.1.0; python_full_version >= '3.7.0'",
            "click==7.1.2",
            "colorama==0.4.6; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6'",
            "distlib==0.3.6",
            "idna==3.4; python_version >= '3.5'",
            "orderedmultidict==1.0.1",
            "packaging==20.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pathspec==0.11.1; python_version >= '3.7'",
            "pep517==0.13.0; python_version >= '3.6'",
            "pip==23.1.2; python_version >= '3.7'",
            "pip-shims==0.7.3; python_version >= '3.6'",
            "pipenv-setup[black]==3.1.4",
            "pipfile==0.0.2",
            "platformdirs==3.5.1; python_version >= '3.7'",
            "plette[validation]==0.4.4; python_version >= '3.7'",
            "pyparsing==3.0.9; python_version >= '3.1'",
            "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "regex==2023.5.5; python_version >= '3.6'",
            "requests==2.30.0; python_version >= '3.7'",
            "requirementslib==1.6.9; python_version >= '3.7'",
            "setuptools==67.7.2",
            "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "toml==0.10.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "tomlkit==0.11.8; python_version >= '3.7'",
            "typed-ast==1.5.4; python_version >= '3.6'",
            "urllib3==1.26.15; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
            "vistir==0.6.1",
            "wheel==0.40.0; python_version >= '3.7'",
        ]
    }
)
