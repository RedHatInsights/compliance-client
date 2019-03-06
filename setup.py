#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup(
        name="compliance-client",
        author="Andrew Kofink <akofink@redhat.com>",
        author_email="akofink@redhat.com",
        license="GPL",
        install_requires=['insights'],
        entry_points={
            'console_scripts': ['compliance-client=compliance_client:main']
        }
    )
