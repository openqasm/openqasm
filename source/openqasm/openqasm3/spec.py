"""
=====================================================
Supported Specification Metadata (``openqasm3.spec``)
=====================================================

.. currentmodule:: openqasm3.spec

Metadata on the specifications supported by this package.

.. autodata:: supported_versions
"""

__all__ = ["supported_versions"]

#: A list of specification versions supported by this
#: package. Each version is a :code:`str`, e.g. :code:`'3.0'`.
supported_versions = [
    "3.0",
    "3.1",
]
