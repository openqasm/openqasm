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
``OPENQASM`` *M.m* ``;`` indicating a major version *M* and minor version *m*.
More details on versioning and the release cycle for OpenQASM may be found
`here <https://github.com/openqasm/openqasm/blob/main/CONTRIBUTING.md>`_.

The minor version number, expressed as a decimal point after the major version
number followed by a number, is optional. If not present, the minor version
number is assumed to be zero.

Multiple occurrences of the version string within a single file are not
permitted, nor may it appear elsewhere than the first non-comment line.
Included files may contain their own version string; see
:ref:`version-headers-in-included-files` below.

Versioning model
----------------

The OpenQASM project uses `semantic versioning (semver) <https://semver.org/>`_:

- **Major version** (e.g., 2 → 3): Backwards-incompatible changes to the
  language. A program written for one major version is generally not valid
  under another.
- **Minor version** (e.g., 3.0 → 3.1): Backwards-compatible additions. All
  features from 3.0 remain valid in 3.1, but 3.1 may introduce new features
  that are not recognized by a 3.0-only parser.
- **Patch version** (e.g., 3.1.0 → 3.1.1): Bug fixes and clarifications to
  the specification text. No language-level feature changes.

The version declaration pins the feature set the file expects. A newer parser
is expected to still accept older declarations within the same major version
(backwards compatibility). The version header is not a minimum-version
specifier; ``OPENQASM 3.0;`` means "exactly the 3.0 feature set," not "any
3.x."

Version parsing behavior
------------------------

The version header declares a pinned specification version. Parsers should
enforce the declared version's feature set and reject programs that violate it.
The following rules define the expected behavior:

1. **Exact version match.** When the declared version matches the parser's
   supported version and no features outside that version are used, the program
   is valid.

   .. code-block::

      // Parser supports up to 3.1
      OPENQASM 3.1;
      // ... uses only 3.0 and 3.1 features ...
      // Result: OK

2. **Feature-version mismatch.** If a program declares a version but uses
   features from a newer minor version, the parser must reject the program or
   emit an error diagnostic citing the declared version.

   .. code-block::

      // Parser supports up to 3.1
      OPENQASM 3.0;
      // ... uses a feature introduced in 3.1 ...
      // Result: Error

3. **Minor version defaults to zero.** When the minor version is omitted, it
   is assumed to be zero. For example, ``OPENQASM 3;`` is equivalent to
   ``OPENQASM 3.0;``.

4. **Missing version header.** The version header is optional. When it is
   absent, the inferred version is implementation-defined. Common strategies
   include: assuming the latest version the parser supports, assuming 3.0 as
   the baseline, or rejecting the program. Parsers should document which
   strategy they use and should emit a warning encouraging the author to add an
   explicit version header.

5. **Declared version exceeds parser support.** If the declared minor version
   exceeds what the parser supports, the parser should reject the program. The
   parser cannot guarantee correct behavior for a version it does not fully
   implement, even if no unrecognized features appear in the file.

   .. code-block::

      // Parser supports up to 3.0
      OPENQASM 3.1;
      // Result: Error (parser cannot guarantee 3.1 compliance)

6. **Unknown major version.** If the declared major version is not supported by
   the parser (e.g., ``OPENQASM 4.0;``), the parser must reject the program.

7. **Major version 2.** When a parser encounters ``OPENQASM 2.0;``, the
   behavior is implementation-defined because the specification does not
   require cross-major-version support. Parsers may choose to reject with a
   clear error, automatically upconvert to OpenQASM 3 constructs, or switch to
   an OpenQASM 2 grammar. Regardless of strategy, the parser must never
   silently interpret OpenQASM 2 syntax under OpenQASM 3 rules or vice versa.
   Parsers should document which strategy they use.

8. **Patch versions in the header.** The grammar only supports ``M.m``, not
   ``M.m.p``. Patch versions are a release and specification management concept,
   not a language-level declaration. A version string such as
   ``OPENQASM 3.0.1;`` is not valid syntax and must be rejected.

9. **Minimum version requirements.** There is no built-in syntax for
   minimum-version ranges. If tooling needs to express compatibility ranges
   (e.g., "this library works with any OpenQASM ≥ 3.0"), that metadata belongs
   outside the ``.qasm`` file, such as in a package manifest, a ``pragma``
   directive, or external toolchain configuration.

Included files
==============

The statement ``include "filename";`` continues parsing ``filename`` as if the
contents of the file were inserted at the location of the ``include`` statement.
This statement can only be used at the global scope.

.. code-block::

   // First non-comment is a version string
   OPENQASM 3.0;

   include "stdgates.inc";

   // Rest of QASM program

The file ``stdgates.inc`` itself is :ref:`the standard library of OpenQASM 3 <standard-library>`.

.. _version-headers-in-included-files:

Version headers in included files
----------------------------------

Included files may contain their own ``OPENQASM M.m;`` version header on their
first non-comment line. This header declares the specification version the
included file was written against, serving as metadata that marks author intent.

When an included file contains a version header, the parser must validate that
the included file's declared version does not exceed the version that was parsed
or inferred from the root file. If the included file declares a higher version
than the root, the parser must reject the program. If the included file declares
a version less than or equal to the root version, the include is valid.

When an included file does not contain a version header, the root file's version
(parsed or inferred) governs the included content.

.. list-table:: Version header scenarios in included files
   :header-rows: 1

   * - Root version
     - Included version
     - Result
   * - ``OPENQASM 3.1;``
     - ``OPENQASM 3.0;``
     - OK (included ≤ root)
   * - ``OPENQASM 3.1;``
     - ``OPENQASM 3.1;``
     - OK (included = root)
   * - ``OPENQASM 3.0;``
     - ``OPENQASM 3.1;``
     - Error (included > root)
   * - ``OPENQASM 3.1;``
     - (none)
     - OK (root version governs)
   * - (none)
     - (none)
     - OK (implementation-defined version governs)
   * - (none)
     - ``OPENQASM 3.0;``
     - Implementation-defined (depends on inferred root version)
