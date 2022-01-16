#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import setuptools

from dbsavior import __version__ as version

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

setuptools.setup(
    name="dbsavior",  # Replace with your own package name
    version=version,
    author="Pengfei Liu",
    author_email="liu.pengfei@hotmail.fr",
    description="This backup restore bot can backup/restore a database and upload/download the backup file to/from"
                " a remote storage engine",
    license='Apache License 2.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pengfei99/K8sCronJobPostgresBackup",
    # we need to indicate excitement which package will be published, otherwise import will raise module name not found
    packages=setuptools.find_packages(include=['dbsavior']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires='>=3.8',

)
