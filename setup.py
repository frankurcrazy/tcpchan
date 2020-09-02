#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "0.1.0"

setuptools.setup(
    name="tcpchan",
    version=version,
    author="Frank Chang",
    author_email="frank@csie.io",
    description="tcpchan is a TCP (de)multiplexer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frankurcrazy/tcpchan",
    packages=setuptools.find_packages(),
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: System :: Networking",
    ],
    keywords=["tcp", "multiplexer", "mux", "stream", "channel"],
    python_requires=">=3.7",
    install_requires=["fpack>=1.0.0",],
)
