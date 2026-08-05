.. _includes:

Included files
==============

The statement ``include "filename";`` incorporates the source unit named by
``filename`` into the program as if its contents were inserted at the location
of the ``include`` statement.  This statement can only be used at the global
scope.

.. code-block::

   // First non-comment is a version string
   OPENQASM 3.0;

   include "stdgates.inc";

   // Rest of QASM program

The file ``stdgates.inc`` itself is :ref:`the standard library of OpenQASM 3 <standard-library>`.


.. _include-resolution:

Resolution
----------

The following terms are used throughout this section.

*Include target*
   The string literal written in an ``include`` statement.  An include target
   is an opaque logical name.  It is not required to be a file-system path, and
   an implementation is not required to interpret it as one.

*Canonical name*
   The identity that resolution associates with a source unit.  Two include
   statements that resolve to the same canonical name refer to the same source
   unit.

*Source unit*
   The OpenQASM source text associated with one canonical name.  The source
   text supplied to an implementation as the program itself is the *root source
   unit*.

Resolution is the process of mapping an include target, together with the
canonical name of the source unit containing the ``include`` statement, to a
canonical name and its source text.  The mechanism an implementation uses to
perform this mapping is implementation defined.  An implementation may resolve
include targets against a file system, against an ordered list of search
locations, against an in-memory table supplied by an embedding host, against
unsaved editor buffers, or by any other means.

Although the mapping is implementation defined, its observable behavior is not.
Within a single compilation of a single program:

* resolving the same include target from the same containing source unit shall
  produce the same canonical name;
* a given canonical name shall produce the same source text;
* an include target that is *relative*, in whatever sense the implementation
  defines relativity, shall be resolved with respect to the canonical name of
  the containing source unit, and shall not be resolved with respect to a
  process working directory or any other ambient state;
* an implementation must diagnose an inclusion cycle; and
* an implementation must support an inclusion depth of at least 15.
  Implementations are encouraged to support considerably more.

These requirements are scoped to a single compilation.  An implementation is
not required to produce the same resolution results across separate
compilations, since the underlying sources may change between them.

An include target must not contain a path component consisting of a single
period ``.`` or a pair of periods ``..``.  An implementation must reject such
an include target.

.. note::

   Resolution is deliberately left implementation defined so that an
   implementation is free to load source from a file system, from a database,
   from an editor's unsaved buffers, from an in-memory table, or from a
   sandboxed environment with no file system at all.  Constraining observable
   behavior rather than the lookup mechanism is what makes all of these
   conforming.

Physical identity
~~~~~~~~~~~~~~~~~

The canonical name is the only notion of source-unit identity defined by this
specification.  Two distinct canonical names denote two distinct source units,
even when an implementation would resolve both to the same underlying storage.

This specification makes no claim about the relationship between a canonical
name and any physical artifact.  In particular it does not require an
implementation to detect that two canonical names refer to the same file
through symbolic links, hard links, case-insensitive file-system behavior,
aliased mount points, or identical content.

.. note::

   Portable detection of physical file identity is not available across the
   environments OpenQASM implementations run in, so requiring it would make
   conformance unattainable for some hosts.  A consequence is that a program
   which reaches the same underlying source through two different canonical
   names will incorporate it twice as two distinct source units.


.. _include-once:

Incorporating a source unit
---------------------------

A source unit shall be incorporated into a program at most once per canonical
name.  When an ``include`` statement resolves to a canonical name that has
already been incorporated into the program, that statement contributes nothing
further to the program.

This rule applies to the source unit as a whole.  It is not limited to
declarations: pragmas, calibration blocks and any other content of a source
unit are incorporated exactly once along with it.

A declaration reached by way of two different ``include`` statements that
resolve to the same canonical name is incorporated once.  A declaration reached
through a different canonical name is incorporated as part of a distinct source
unit.  The include mechanism does not itself define any additional declaration
collision rule beyond the ordinary name, scope and overloading rules of the
language.

.. code-block::
   :caption: File ``a.inc``

   include "stdgates.inc";
   gate my_a q { h q; }

.. code-block::
   :caption: File ``b.inc``

   include "stdgates.inc";
   gate my_b q { x q; }

.. code-block::
   :caption: Main program

   OPENQASM 3.0;

   include "a.inc";
   include "b.inc";

   // Valid.  `stdgates.inc` is incorporated once, by the first `include`
   // statement that resolves to it.  The second inclusion contributes
   // nothing, so `h`, `x` and the other standard gates are each declared
   // exactly once.  Both `my_a` and `my_b` are in scope.

Calibration definitions
~~~~~~~~~~~~~~~~~~~~~~~

As described in :ref:`the section on scoping <scope-global>`, multiple
``defcal`` statements may affect the same operation; this is overloading rather
than redeclaration.  ``defcal`` statements originating from different source
units overload one another in exactly the same way as ``defcal`` statements
written in a single source unit.

Repeated inclusion
~~~~~~~~~~~~~~~~~~

There is no mechanism for incorporating the same source unit into a program
more than once.  A source unit intended to contribute different content at
different points of a program cannot be expressed by repeated inclusion.

Source units that are not self-contained
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As described in :ref:`the section on scoping <scope-global>`, an included
source unit is parsed in the scope that included it, and may therefore refer to
identifiers declared by its containing source unit.  Such a source unit is
incorporated at the first ``include`` statement that resolves to it, and the
identifiers in scope at that point are the ones it sees.

A source unit that refers to identifiers declared by its containing source unit
is therefore not suitable for inclusion from more than one place.  Source units
intended to be included by more than one other source unit should be
self-contained.


.. _include-host-integration:

Note on host integration
------------------------

.. note::

   This section is non-normative.  It describes a common shape for the
   interface between an implementation and an embedding host, so that programs
   and tooling are portable across implementations in practice.  Nothing in
   this section constrains conformance.

Because resolution is implementation defined, an implementation embedded in a
larger application typically exposes resolution as an extension point.  Four
forms cover the environments OpenQASM implementations are commonly embedded
in, and implementations are encouraged to offer all four:

1. *No resolver.*  Include targets are not resolved and no source is loaded.
   The ``include`` statement is retained in whatever representation the
   implementation produces.  This is the appropriate default for a tool that
   only parses or formats a single source unit.

2. *A mapping.*  The host supplies a mapping from canonical name to source
   text.  This suits notebooks, test harnesses, virtual file systems, and any
   host that already holds all candidate sources in memory.

3. *A callable.*  The host supplies a function that receives the include
   target and the canonical name of the containing source unit, and returns
   the source text together with the canonical name it resolved to, or an
   indication that the target is not one it handles.  Both inputs are
   necessary: without the containing source unit's canonical name, a relative
   include target cannot be resolved.

4. *A resolver object.*  The host supplies an object implementing the same
   contract as the callable, which additionally allows several resolvers to be
   composed so that each is consulted in turn.

An implementation that loads source from a file system should treat that
capability as something the host opts into, rather than as default behavior,
and should restrict it to locations the host has designated.  Include targets
may originate from untrusted source text.
