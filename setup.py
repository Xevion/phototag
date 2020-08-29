"""
setup.py

The installation script responsible for setting up the CLI program on the user's system.
"""

import os
import sys

from setuptools import find_packages, setup

DEPENDENCIES = [
    "Click",
    "rawpy",
    "imageio",
    "iptcinfo3",
    "google-api-python-client",
    "google-cloud",
    "google-cloud-vision",
    "Pillow",
    "colored-traceback",
    "ImageHash",
    "rich"
]
EXCLUDE_FROM_PACKAGES = []
CURDIR = sys.path[0]

with open(os.path.join(CURDIR, "README.md")) as file:
    README = file.read()

setup(
    name="phototag",
    version="1.0.0",
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
        phototag=phototag.cli:cli
    """,
    zip_safe=False,
    install_requires=DEPENDENCIES,
    python_requires=">=3.6",
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
