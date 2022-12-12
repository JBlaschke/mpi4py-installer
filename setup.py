#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="mpi4py-installer",
    version="0.3.0",
    author="Johannes Blaschke",
    author_email="jblaschke@lbl.gov",
    description="No more copy+paste of magic bash commands while installing mpi4py on HPC systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JBlaschke/mpi4py-installer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
)
