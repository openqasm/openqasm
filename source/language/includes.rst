.. _includes:

Included source units
=====================

The statement ``include "target";`` incorporates the source unit named by
``target`` into the program as if its contents were inserted at the location
of the ``include`` statement.  This statement can only be used at the global
scope.

.. code-block::

   // First non-comment is a version string
   OPENQASM 3.0;

   include "stdgates.inc";

   // Rest of QASM program

The source unit ``stdgates.inc`` itself is :ref:`the standard library of OpenQASM 3 <standard-library>`.


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
canonical name and its source text.  It has two parts.  Which canonical names
an include target may name is specified below, under
:ref:`include-candidates`.  Where the source text for a canonical name comes
from is implementation defined: an implementation may hold source in a file
system, in an in-memory table supplied by an embedding host, in an editor's
unsaved buffers, in a database, or anywhere else.

Although the mapping is implementation defined, its observable behavior is not.
Within a single compilation of a single program:

* resolving the same include target from the same containing source unit shall
  produce the same canonical name;
* a given canonical name shall produce the same source text;
* an include target shall be resolved with respect to the canonical name of the
  containing source unit and the library map that applies to it, as described
  under :ref:`include-candidates`, and shall not be resolved with respect to a
  process working directory or any other ambient state;
* an implementation must diagnose an inclusion cycle.

These requirements are scoped to a single compilation.  An implementation is
not required to produce the same resolution results across separate
compilations, since the underlying sources may change between them.

An implementation may limit how deeply inclusion nests.  Any such limit, and
whether it is reached, is implementation defined.


.. _include-candidates:

Candidate names
~~~~~~~~~~~~~~~

Resolution forms *candidate canonical names* for an include target and asks
which of them names a source unit.

The *library root* of a canonical name is the part of it up to and including
its first ``/`` when the name begins with ``@``, and is empty otherwise.  A
library groups source units that are maintained together, such as one obtained
from elsewhere, and is written into the canonical name itself so that a source
unit carries its library with it.

A target naming another library is resolved through a *library map*, described
under :ref:`include-library-names`, so that form needs state beyond the two
names it is given.  Every other form is formed from those two names alone.

For an include target ``T`` written in a source unit whose canonical name is
``I``, the candidate canonical names are

* ``T`` alone, when ``T`` is ``stdgates.inc``, which is reserved as the
  canonical name of :ref:`the standard library <standard-library>`;
* what the applicable library map gives for ``T``, when ``T`` begins with
  ``@``, as described under :ref:`include-library-names`;
* the library root of ``I`` followed by the rest of ``T``, when ``T`` begins
  with ``//``;
* otherwise both the prefix of ``I`` up to and including its last ``/``,
  or nothing when ``I`` has no ``/``, followed by ``T``, and the library root of
  ``I`` followed by ``T``.

.. table:: [include-candidates] candidate canonical names, by the form of the include target and
   the canonical name of the source unit that writes it.

   ========================  ==================  ========================================
   Written in                Target              Candidates
   ========================  ==================  ========================================
   ``main.qasm``             ``x.inc``           ``x.inc``
   ``lib/main.qasm``         ``x.inc``           ``lib/x.inc``, ``x.inc``
   ``lib/main.qasm``         ``//x.inc``         ``x.inc``
   ``@vendor/gates.inc``     ``x.inc``           ``@vendor/x.inc``
   ``@vendor/sub/g.inc``     ``x.inc``           ``@vendor/sub/x.inc``, ``@vendor/x.inc``
   ``@vendor/sub/g.inc``     ``//x.inc``         ``@vendor/x.inc``
   any source unit           ``@other/x.inc``    per the applicable library map
   any source unit           ``stdgates.inc``    ``stdgates.inc``
   ========================  ==================  ========================================

The first two rows are the ordinary cases: a target beside its includer, and a
target that also exists at the root.  The rows beginning ``@vendor`` are the
same two cases inside a library.  A source unit does not declare the library it
belongs to; ``@vendor/`` is the library root its canonical name already
carries, and resolution reads it from there.  This is why a library resolves
its own names without reaching the program that uses it.

.. note::

   The reserved standard-library name is not scoped to a library, so a source
   unit inside a library includes the standard library exactly as any other
   source unit does.  Without that reservation a library could not use the
   standard library at all, because every candidate it formed would name a
   source unit within itself.

Exactly one candidate shall name a source unit.  When none does, the include
target cannot be resolved.  When more than one does and they are distinct
canonical names, the include target is *ambiguous* and an implementation shall
diagnose it.

For example, in a program containing source units ``lib/main.qasm``,
``lib/helper.inc`` and ``helper.inc``, the statement ``include "helper.inc";``
written in ``lib/main.qasm`` has two candidates that each name a source unit,
so it is ambiguous.  Writing ``include "//lib/helper.inc";`` or
``include "//helper.inc";`` names one of them and resolves.

.. note::

   Because an ambiguous target is diagnosed rather than resolved, the candidates
   need no relative precedence; only the set matters.  An author who is told a
   target is ambiguous says which source unit is meant by writing it in the
   ``//`` form, which always yields one candidate.

   Scoping the second candidate to the includer's library root, rather than
   to the whole program, is what keeps a source unit in one library from
   reaching into another.  A library cannot silently absorb a source unit
   belonging to the program that uses it, and adding a source unit to a library
   cannot change what the using program resolves.

An implementation must reject an include target that

* is empty;
* contains a path component consisting of a single period ``.`` or a pair of
  periods ``..``;
* contains an empty path component, as in ``a//b``;
* begins with ``/``, other than the ``//`` form described above;
* names a library but no source unit within it, as in ``@library``;
* combines ``//`` with a library, as in ``//@library/name``;
* contains a ``\`` character; or
* begins with a drive specifier, such as ``C:``, whether or not it is written
  after ``//``.

.. note::

   An include target is an opaque logical name, so these forms are not rejected
   because they are bad paths.  They are rejected because they are the forms
   whose meaning differs between the environments implementations run in: ``\``
   separates components on one family of systems and is an ordinary filename
   character on another, ``C:rel`` is resolved against a per-drive working
   directory, and an absolute target names a location that cannot exist on
   another machine.  Accepting them would make a program's meaning depend on
   the system compiling it.

   OpenQASM string literals have no escape sequences, so a backslash written in
   an include target is a literal backslash.  ``include "lib\gates.inc";`` is
   well-formed as a token and is rejected at resolution.

.. note::

   Where source text comes from is deliberately left implementation defined, so
   that an implementation is free to load it from a file system, from a
   database, from an editor's unsaved buffers, from an in-memory table, or from
   a sandboxed environment with no file system at all.  Specifying the names an
   include target may take, while leaving the lookup itself open, is what lets
   all of these be conforming and still gives one program the same meaning on
   each of them.

.. _include-library-names:

Apparent and canonical library names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library name written in an include target is an *apparent name*.  It is
chosen by whoever wrote the source unit that uses the library, and it is
meaningful only within that source unit's own library.  The library name
carried by a canonical name is a *canonical library name*, and it identifies
one library throughout a program.  Neither form includes the ``@`` or the
``/`` around it, which are selector syntax rather than part of a name.

A *library map* maps apparent names to canonical library names.  There is at
most one library map for each library, and at most one for the program itself.
The library map that applies to an include target is the one belonging to the
library of the source unit that writes it; a source unit that is not in a
library uses the program's own library map.  Where library maps come from is
implementation defined, exactly as the source text for a canonical name is.

For an include target ``T`` beginning with ``@``, let ``A`` be the text between
``@`` and the first ``/``, and let ``R`` be the rest of ``T`` after that ``/``.
The candidate canonical names are

* ``T`` alone, when the implementation is given no library maps at all;
* otherwise ``@C/R``, where ``C`` is the canonical library name the applicable
  library map gives for ``A``;
* otherwise none at all, which covers both a source unit whose library has no
  map and an applicable map that gives no canonical library name for ``A``.

.. table:: [include-library-names] candidate canonical names for a library
   target ``@v/x.inc``, by the library map that applies to the source unit that
   writes it.

   ==========================================  ==================
   Applicable library map                      Candidates
   ==========================================  ==================
   no library maps at all                      ``@v/x.inc``
   none for the includer's library             none
   ``{v: vendor}``                             ``@vendor/x.inc``
   ``{v: v}``                                  ``@v/x.inc``
   ``{}``                                      none
   ``{w: other}``                              none
   ==========================================  ==================

Being given no library maps at all and being given an empty one are distinct
states and shall not be conflated.  The first is a host that does not scope
library names, and every apparent name is then its own canonical name.  The
second is a source unit that has been given no libraries, and no apparent name
resolves for it.

An apparent name the applicable library map does not give a canonical library
name for names no source unit.  It is not ill formed, and shall be diagnosed as
an unresolved include target rather than as an invalid one.

.. note::

   Two levels of naming exist because a library name written in source text
   cannot be both stable and globally unique.  If a program had to write the
   one true name of every library it uses, then two libraries that had
   independently chosen the same name could never be used together, and
   renaming a library would break every program that reaches it through another
   library.  Separating what a source unit writes from what identifies a
   library lets one program choose its own spelling for each library it uses,
   and lets two libraries use one spelling for different libraries.

.. note::

   Because the applicable library map is the one belonging to the source unit
   that writes the target, a source unit reaches only the libraries its own
   library map names.  A library cannot make its own libraries reachable from
   the program that uses it, since the program's library map is the only one
   consulted for a target the program writes.

Physical identity
~~~~~~~~~~~~~~~~~

The canonical name is the only notion of source-unit identity defined by this
specification.  Two distinct canonical names denote two distinct source units,
even when an implementation would resolve both to the same underlying storage.

This specification makes no claim about the relationship between a canonical
name and any physical artifact.  In particular it does not require an
implementation to detect that two canonical names refer to the same file
through symbolic links, hard links, case-insensitive file-system behavior,
aliased mount points, or identical content.  An implementation may collapse
some of them, as one that resolves symbolic links before forming a canonical
name does, but this specification prescribes no portable behavior in these
cases.

.. note::

   Not every environment an OpenQASM implementation runs in has a file system
   to ask: source may come from an in-memory table, an editor's unsaved
   buffers, a database, or a sandbox with no file system at all.  Where there
   is one, identity is not reliably comparable across network and overlay file
   systems.  Requiring detection would therefore make conformance unattainable
   for some hosts.  A consequence is that a program which reaches the same
   underlying source through two different canonical names will incorporate it
   twice as two distinct source units.


.. _include-once:

Incorporating a source unit
---------------------------

A source unit shall be incorporated into a program at most once per canonical
name.  When an ``include`` statement resolves to a canonical name that has
already been incorporated into the program, that statement contributes nothing
further to the program.

.. _include-order:

Order of incorporation
~~~~~~~~~~~~~~~~~~~~~~

The ``include`` statements of a source unit are considered in the order they
appear in its source text.  When an ``include`` statement resolves to a
canonical name that has not already been incorporated, that source unit is
incorporated at that point.  The newly reached source unit, including every
source unit reached through its own ``include`` statements, is incorporated
before consideration returns to the next ``include`` statement of the
including source unit.

For example, consider these source units:

.. code-block::
   :caption: Source unit ``A``

   include "B";
   include "C";

.. code-block::
   :caption: Source unit ``B``

   include "D";

The source units are incorporated in this order:

1. ``A``, the root source unit.
2. ``B``, reached by the first ``include`` statement in ``A``.
3. ``D``, reached by the ``include`` statement in ``B``.
4. ``C``, reached after consideration returns to the second ``include``
   statement in ``A``.

.. note::

   Algorithmically, incorporation follows a depth-first preorder traversal.
   Starting with the root source unit, visit each ``include`` statement in
   source order.  When a statement reaches a source unit that has not already
   been incorporated, incorporate that source unit and recursively visit its
   ``include`` statements before continuing with the next statement in the
   including source unit.

.. note::

   Order is specified because it is observable.  A source unit that is not
   self-contained sees the identifiers that are in scope where it is
   incorporated, so incorporating source units in a different order would give
   the same program a different meaning.

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
   :caption: Source unit ``a.inc``

   include "stdgates.inc";
   gate my_a q { h q; }

.. code-block::
   :caption: Source unit ``b.inc``

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
larger application typically exposes resolution as an extension point.  The
source-lookup part commonly has four forms, and implementations are encouraged
to offer all four:

1. *No resolver.*  Include targets are not resolved and no source is loaded.
   The ``include`` statement is retained in whatever representation the
   implementation produces.  This is the appropriate default for a tool that
   only parses or formats a single source unit.

2. *A mapping.*  The host supplies a mapping from canonical name to source
   text.  This suits notebooks, test harnesses, virtual file systems, and any
   host that already holds all candidate sources in memory.

3. *A callable.*  The host supplies a function that receives one canonical name
   and returns the source text for it, together with the canonical name it
   resolved to, or an indication that it does not supply that source unit.  The
   implementation forms the candidate canonical names described under
   :ref:`include-candidates` before calling, so a host does not implement the
   naming rules itself.

4. *A resolver object.*  The host supplies an object implementing the same
   contract as the callable, which additionally allows several resolvers to be
   composed so that each is consulted in turn.

An embedding interface should bind source lookup and any library maps into one
complete resolution environment.  They remain distinct responsibilities within
that environment: a resolver is asked for canonical names only, while the
translation described under :ref:`include-library-names` happens before any
resolver is consulted.  A host that composes resolvers does not implement that
translation itself.  An environment with no library maps gets the fallback in
which an apparent name is its own canonical name, which is what a host holding
one flat table of source units wants.

An implementation that loads source from a file system should treat that
capability as something the host opts into, rather than as default behavior,
and should restrict it to locations the host has designated.  Include targets
may originate from untrusted source text.
