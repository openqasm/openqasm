Comments
========

Comments begin with a pair of forward slashes ``//`` and end with a new line:

.. code-block:: c

   // A comment line

A comment block begins with ``/*`` and ends with ``*/``:

.. code-block:: c

   /*
   A comment block
   */

Version string
==============

The first non-comment line of an OpenQASM program may optionally be
``OPENQASM`` *M.m* ``;`` indicating a major version *M* and minor version *m*.

This document describes Version 3.0.

The minor version number, expressed as a decimal point after the major version
number followed by a number, is optional. If not present, the minor version
number is assumed to be zero.

Multiple occurrences of the version string (outside of comments) are not
permitted, nor may it appear elsewhere than the first non-comment line.

Included files
==============

The statement ``include "filename";`` continues parsing ``filename`` as if the
contents of the file were inserted at the location of the ``include`` statement.

.. code-block:: c

   // First non-comment is a version string
   OPENQASM 3.0;

   include "stdgates.qasm";

   // Rest of QASM program
