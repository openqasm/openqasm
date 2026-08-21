Comments
========

Comments begin with a pair of forward slashes ``//`` and end with a new line:

.. code-block::

   // A comment line

A comment block begins with ``/*`` and ends with ``*/``:

.. code-block::

   /*
   A comment block
   */


.. _version-string:

Version string
==============

The first non-comment line of an OpenQASM program may optionally be
``OPENQASM`` *M.m* ``;`` indicating a major version *M* and minor version *m*.
More details on versioning and the release cycle for OpenQASM may be found
`here <https://github.com/openqasm/openqasm/blob/main/CONTRIBUTING.md>`_.

The minor version number, expressed as a decimal point after the major version
number followed by a number, is optional. If not present, the minor version
number is assumed to be zero.

Multiple occurrences of the version string within a source unit (outside of
comments) are not permitted, nor may it appear elsewhere than the first
non-comment line.  An included source unit may contain its own version string.

The root source unit establishes the effective version of the program.  If the
root has no version string, its effective version is OpenQASM 3.0.  An
implementation that does not support OpenQASM 3.0 must reject the source unit
rather than interpret it under another version.  Implementations should emit a
diagnostic when applying this default.  The root effective version governs
language interpretation and feature availability in every source unit.

An included source unit may contain a version string as metadata recording the
author's intended language version.  After applying the optional-minor rule,
that version must not be greater than the root effective version.  The
declaration neither establishes another effective version nor changes how the
source unit is interpreted, and is not textually incorporated as another
program-level version statement.  A headerless included source unit inherits
the root effective version.  These rules are independent of the immediately
containing source unit and the first inclusion path.
