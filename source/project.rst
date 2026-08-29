.. _project:

Project definition
==================

.. note::

   This document is non-normative.  It describes a conventional way for a host
   to decide which source units make up a compilation and what canonical names
   they are given, so that programs and tooling are portable across
   implementations in practice.  Nothing in this document constrains
   OpenQASM language conformance, and nothing in it changes the meaning of any
   program.  A host may claim compatibility with this project profile
   separately.

:ref:`Include resolution <include-resolution>` maps an include target, together
with the canonical name of the including source unit, to a canonical name and
its source text.  The mapping is deliberately implementation defined, so that a
filesystem, an in-memory table, an editor's unsaved buffers, a notebook, or a
sandboxed environment with no file system at all can each be conforming.

That leaves one question open in practice: where does a host get its canonical
names and its source text?  A *project* answers it.  A project is a set of source
units rooted at one directory, the *project root*.  Usually the host identifies
that root by finding a manifest there; a caller may instead designate the root
explicitly, and single-file mode creates a minimal project context without a
manifest.  A host loads the project, produces a finite mapping from canonical
name to source text and owner-local library bindings, and supplies both as one
resolution environment through the load behaviors described in
:ref:`the note on host integration <include-host-integration>`.

Nothing about resolution changes.  The manifest only makes the host's inputs
explicit rather than ambient.


.. _project-manifest:

The manifest
------------

The manifest is a file named ``openqasm.json`` in the project root.
It is a single JSON object.  An empty object ``{}`` is a valid manifest and
means "this directory is a project, with defaults for everything".

Format
~~~~~~

The manifest is JSON as specified by :rfc:`8259`, with the following
restrictions, each of which exists because two widely used standard-library
parsers otherwise disagree:

* The encoding is UTF-8 with no byte-order mark.
* The top-level value is an object.
* ``NaN``, ``Infinity`` and ``-Infinity`` are not permitted, even where a parser
  would accept them.
* A duplicate key within one object is an error, rather than last-one-wins.
* An integer of magnitude greater than 2\ :sup:`53`\ -1 is rejected wherever it
  appears, including under a key the loader does not recognize.

JSON has no comment syntax.  A ``$comment`` key whose value is a string may
appear in any object whose keys this document fixes.  It carries no meaning, and
a loader may discard it.

``libraries`` is the exception, because its keys are names its author chooses
rather than names this document fixes.  A ``$comment`` there declares a library
called ``$comment``, and nothing can tell that apart from an annotation.  A note
about one library belongs inside that library's own object, whose keys this
document does fix.

Fields
~~~~~~

Every field is optional.

.. list-table::
   :header-rows: 1
   :widths: 14 16 70

   * - Key
     - Type
     - Meaning
   * - ``$schema``
     - string
     - A hint for editors.  A loader ignores it.
   * - ``$comment``
     - string
     - Carries no meaning.  Permitted in any object whose keys this document
       fixes, which is every object except ``libraries``.
   * - ``files``
     - array of string
     - The exhaustive set of source files, each a project-relative name as
       defined below.  When absent, the default file set is used instead.
   * - ``programs``
     - array of string
     - The source units the project offers for compilation, each a
       project-relative source name that is a member of the file set.  See
       :ref:`project-programs`.
       When absent, a host derives them.  An empty array declares that the
       project offers none, which is what a project used only as a
       :ref:`library <project-libraries>` does.
   * - ``libraries``
     - object
     - The libraries this project depends on, each mapping the name this
       project writes for a library to where that library comes from.  See
       :ref:`project-libraries`.
   * - ``name``
     - string
     - The name this project is known by when another project uses it as a
       library.  A project used only on its own needs none; a project used as
       a library must declare one.  See :ref:`project-libraries`.

A loader ignores a key it does not recognize.  There is no manifest-version
field; the manifest evolves by gaining optional keys that add information but
do not change the meaning of fields an older loader understands.

.. code-block:: json
   :caption: A manifest

   {
     "$schema": "https://openqasm.com/_static/schemas/openqasm-project-v1.schema.json",
     "files": [
       "programs/qec_round.qasm",
       "lib/gates/extra.inc",
       "lib/gates/helpers.inc"
     ],
     "programs": [
       "programs/qec_round.qasm"
     ]
   }


.. _project-discovery:

Finding the project
-------------------

A host that is given a source file and asked to compile it locates the project
in this order:

1. A manifest path supplied by the caller is used directly.
2. A project root supplied by the caller is used directly.  A manifest, if any,
   must be immediately inside it.
3. Otherwise the host searches upwards from the directory containing the file.
4. If the search finds nothing, the file is compiled in *single-file mode*.

The upward search examines a directory only when the host has not supplied
*workspace roots*, or when the directory is inside one of them.  A workspace
root is a directory the host has explicitly designated as open; it is a search
boundary and need not be a project root.  A directory the search
examines is tested against these conditions, in order:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Condition
     - Result
   * - The directory contains ``openqasm.json``
     - That directory is the project root.
   * - The directory contains ``.git``, ``.hg``, ``.svn`` or ``.jj``
     - Stop.  There is no project.
   * - The directory is the user's home directory
     - Stop.  There is no project.
   * - The directory has no parent
     - Stop.  There is no project.
   * - 64 directories have been examined
     - Stop.  There is no project.

The workspace test comes first so that a manifest above the workspace cannot
capture a file inside it; a host that opens one folder does not acquire a
project from its parent.  Within a directory that is examined, the manifest test
precedes the version-control test, so a manifest at the root of a repository is
found.  The remaining conditions exist because an unbounded upward search reads
files the user did not intend to expose; a host that has an ownership or trust
signal available should apply it as a further stop condition.

A manifest that cannot be parsed is an error.  The search does not continue past
it, because continuing would let a typo silently move a file into a different
project.

Nested projects
~~~~~~~~~~~~~~~

The nearest manifest wins, and a nested manifest ends the extent of the project
above it.  Manifests do not combine, and there is no inheritance between them.

Single-file mode
~~~~~~~~~~~~~~~~

When no manifest is found, single-file mode applies to the specific file being
compiled.  It uses the directory containing that file as a synthetic project
root.  The file set is exactly that one file, and its canonical name is its base
name.  A canonical name with no ``/`` has no name prefix, so an include target
written in that file is tried on its own.

This fallback is local to the target file: it does not extend to
sibling files, it does not absorb a parent project, and it is not a host-global
setting inherited from nearby directories.  A host must evaluate it per
compilation target, and a discovered project must always override it for the
file it covers.

This is what an implementation does today for a lone source file, and it is why
introducing a manifest cannot change the meaning of a program that does not have
one.


.. _project-file-set:

The file set
------------

When ``files`` is present it is the file set, in the order written.

When ``files`` is absent the file set is produced by walking the project root
with the following procedure.  It is given as a procedure rather than as a
pattern because pattern matching is not portable: two widely used
standard-library implementations differ on case sensitivity, on brace
expansion, on whether hidden entries are matched, on result ordering, and on
whether ``**`` follows symbolic links.

Starting at the project root, and for each directory:

1. List the directory's entries.
2. Sort them by their names compared as sequences of UTF-8 code units,
   ascending.
3. Skip an entry whose name begins with ``.``.
4. Skip an entry whose name begins with ``@``.
5. Skip an entry that is a symbolic link, without resolving it.
6. Skip a directory that holds a file named ``openqasm.json``, or that contains
   an entry named ``.git``, ``.hg``, ``.svn`` or ``.jj``, without recursing into
   it.
7. Recurse into any other entry that is a directory.
8. Otherwise, include the entry when its name ends in ``.qasm`` or ``.inc``,
   compared case-sensitively.

Step 4 keeps the walk from minting a name only a ``libraries`` declaration may
mint, and step 5 keeps one file from entering the file set under two names.

Step 6 is the walk's boundary, and it is the same boundary the upward search
uses.  A nested manifest ends the extent of the project above it, so a walk that
descended past one would give the enclosing project files that discovery assigns
to the nested project: the two directions would disagree about which project a
file belongs to.  The version-control markers are listed rather than described
because a vendored checkout is a repository of its own, and a host that guessed
at the set would absorb a different set of files than another host.  The markers
are tested for existence, not for being directories, because a worktree or a
submodule records ``.git`` as a file; ``openqasm.json`` must itself be a file.  The project root itself is not tested; a
project's own manifest does not end its own walk.

The sort is specified because neither directory listing nor pattern matching
guarantees an order in the environments implementations run in, and an
unspecified order makes the file set unstable between hosts.

This order makes file-set construction deterministic.  It does not require a
loaded project's canonical-name mapping to expose any order.

.. _project-portable-names:

Portable name policy
--------------------

The three kinds of name defined by a project share one character and Unicode
policy.  Their structures and collision scopes differ:

.. list-table::
   :header-rows: 1
   :widths: 20 30 25 25

   * - Name domain
     - Structure
     - Characters and spelling
     - Collision scope
   * - Project-relative source name
     - A nonempty relative POSIX path: no leading ``/`` or ``\``, drive
       qualification, ``\``, empty component, ``.`` or ``..`` component, or
       component beginning with ``@``.
     - The exact Unicode spelling is retained.  ``[``, ``]``, ``{`` and ``}``
       are ordinary characters; ``*`` and ``?`` are forbidden.
     - Across the loaded canonical-name mapping, exact, ASCII-case-only, and
       NFC-equivalent collisions are errors.
   * - Apparent library name
     - A nonempty component: no leading ``@``, separator, ``.`` or ``..``.
     - The exact Unicode spelling is retained.  ``[``, ``]``, ``{`` and ``}``
       are ordinary characters; ``*`` and ``?`` are forbidden.
     - Within one project's ``libraries`` object, NFC-equivalent spellings are
       an error.  Apparent names in different projects are independent.
   * - Canonical library name
     - A nonempty component: no leading ``@``, separator, ``.`` or ``..``.
     - The exact Unicode spelling is retained.  ``[``, ``]``, ``{`` and ``}``
       are ordinary characters; ``*`` and ``?`` are forbidden.
     - Across one load, NFC-equivalent spellings are an error, and one exact
       name cannot bind two different library roots.


.. _project-canonical-names:

Canonical names
---------------

Within this project convention, each file-set entry is a *project-relative
source name*: its location relative to the project root, expressed with ``/``
as the separator.  Once the entry is validated, the host assigns it unchanged
as the source unit's canonical name.  This is one host convention for assigning
the abstract source-unit identity defined by
:ref:`include resolution <include-resolution>`; other resolvers need not derive
canonical names from file-system locations.

Two canonical names are the same when their strings are identical.  Nothing is
folded and nothing is normalized: a name is the sequence of characters the host
supplied, and transforming it would assert an equivalence the file system does
not guarantee.  The rejection of equivalent declarations is separate from
rewriting a name; the shared rules and their scopes are stated under
:ref:`project-portable-names`.

The consequences are these:

Case
  Two entries are an error, reported when the project is loaded, if their
  canonical names become identical once the ASCII letters ``A`` to ``Z`` are
  lowered.  A difference that survives that fold is not a collision, so two
  names differing only by non-ASCII case, such as ``\u03c3`` and ``\u03a3``,
  are two source units.  The fold is restricted to ASCII because implementation
  languages do not offer the same full case folding: one folds ``ß`` to ``ss``
  and another offers no such operation at all.  Restricting the fold is what
  lets two implementations agree on the same answer.  A loader does not
  attempt to detect whether the underlying volume is case-insensitive.

Normalization
   A name is never normalized or rewritten, and a ``files`` entry must be
   written the way the volume stores it.  NFC is used only to detect when two
   spellings in the applicable collision scope are canonically equivalent; the
   pair is rejected with
   ``canonical-name-normalization-collision``.  Either spelling is retained
   unchanged when it occurs alone.

   A non-ASCII file name remains only as portable as the volumes it is stored
   on: a volume that normalizes names on creation presents a different spelling
   from one that preserves what it is given.  Collision detection prevents one
   project from assigning both spellings, but it does not make an isolated name
   portable between those volumes.  A project that needs its names to be
   portable everywhere should keep them to ASCII.

Symbolic links
   A canonical name is never derived from a resolved path, and the walk never
   traverses a symbolic link.  Resolving links is used only to check
   containment, described below.  Keeping the two apart is what makes a
   canonical name portable between machines and between a filesystem host and a
   host holding unsaved editor buffers.

Absolute paths
   A canonical name is never absolute.

The reserved name
   :ref:`The standard library's canonical name <standard-library>` is reserved.
   A project file whose canonical name would be ``stdgates.inc`` is an error,
   because an implementation resolves that target before consulting any
   host-supplied mapping, so such a file could never be reached.  Diagnosing it
   is better than silently carrying source that nothing can reach.

   The file a host was asked to compile is the exception.  It was not reached
   by resolving a target, so the reason for the restriction does not apply to
   it, and refusing it would leave a host unable to open a file by name.  The
   exemption covers that one canonical name in that one compilation; the same
   file included from elsewhere still resolves to the standard library.

The reserved prefix
   A project-relative source name may not have a component beginning with
   ``@``, and the default walk skips such an entry.  ``@`` introduces a
   :ref:`library <project-libraries>` in a canonical name, and only a
   ``libraries`` declaration mints one.  Without the reservation a directory
   name would decide whether its contents form a library, so renaming a
   directory would change what the source units inside it resolve.


.. _project-containment:

Containment
-----------

Every file the loader reads must lie inside the root that supplies it.  For a
project's own files that root is the project root; for a library's files it is
that :ref:`library's root <project-libraries>`.  To decide containment for a
candidate path:

1. Resolve symbolic links in the supplying root, once.
2. Resolve symbolic links in the candidate.  A candidate that does not exist is
   resolved through its last existing component; the remainder is appended
   without further resolution.
3. Compute the candidate's location relative to the resolved root.
4. Accept only when that relative location is not absolute and does not begin
   with a ``..`` component.

A textual prefix test is not sufficient and must not be used: ``/ab/c`` begins
with the text ``/a`` but is not inside the directory ``/a``.

The project root is the manifest's own directory, and a project has exactly one.
A declared library is a separate project with a root of its own, and the roots
taking part in one load are disjoint, for the reason given under
:ref:`project-libraries`.  Where two files would produce the same canonical
name, a loader reports an error rather than choosing one.

The specification requires an include target to be portable, so one that is
empty, absolute, drive-qualified, or that contains a ``\`` character or a
``.``, ``..`` or empty path component is rejected before any resolver is
consulted.  See :ref:`include-resolution`.  A project adds no further
restriction on include targets: what a project needs here is what portability
already requires of every implementation.


.. _project-resolver:

Supplying the project to an implementation
------------------------------------------

Having established the file set and the canonical names, a host builds a finite
mapping from canonical name to source text:

.. code-block:: text

   for each name in the file set:
       require the file is contained in the project root
       require the name is not the reserved standard-library name
       require the name has not already been used
       map[name] := the file's text, read as UTF-8

Three properties follow without further work:

* A relative include target resolves against its includer, because one of the
  candidate names formed from a target carries the including source unit's name
  prefix.
* The standard library is unaffected, because an implementation resolves its
  reserved name ahead of any host-supplied mapping.
* An ambiguous project is rejected rather than silently resolved, because
  building the mapping eagerly makes a duplicate canonical name an error.

The host binds this mapping and each project's apparent-to-canonical library
names into one resolution environment.  Supplying them separately would permit
source lookup from one loaded project to be paired with visibility rules from
another.  An implementation may represent the environment however it chooses.

The Python reference package exposes an immutable
:class:`openqasm3.project.LoadedProject` snapshot.  Its ``sources`` and nested
``library_bindings`` mappings are read-only, and its ``environment`` is built
from those same snapshots.  :func:`openqasm3.parse_project` selects an explicit
source name or the loaded compilation root and rejects an absent or unknown
selection before parsing.  When ``programs`` is absent,
:func:`openqasm3.derive_programs` accepts the loaded project and derives roots
from its finite inventory.  Loading remains available without parser support.

A host that must load lazily, or that must prefer an editor's unsaved buffer
over the text on disk, supplies a callable or a resolver object instead.  It
applies the same naming rules, consults its buffers first and the file set
second, and indicates that a name outside the file set is not one it handles.
A host that only formats or syntax-checks one source unit supplies no resolver
at all.


.. _project-inclusion-depth:

Inclusion depth
~~~~~~~~~~~~~~~

An implementation that follows this document accepts inclusion nested at least
fifteen deep.  The language leaves any depth limit implementation defined, so
this floor is fixed here for independent hosts to agree on.  A host may support
more.  A project that nests deeper than the host supports is diagnosed rather
than silently truncated.


.. _project-libraries:

Libraries
---------

A *library* is a project used by another project.  The ``libraries`` field maps
the name this project writes for a library to where that library comes from.
The ``@`` character is not part of either name; it introduces the library
selector in a canonical name or include target:

.. code-block:: json
   :caption: Depending on a library

   {
     "libraries": {
       "vendor": { "path": "../shared/vendor" }
     }
   }

.. code-block:: json
   :caption: The library, declaring the name it is known by

   {
     "name": "vendor"
   }

Two names are in play.  The
key in ``libraries`` is the *apparent name*: what this project writes, chosen by
whoever wrote this manifest.  The library's own ``name`` is the *canonical
library name*: what identifies the library in every canonical name its files
take.  They are written the same way and may be the same string, as they are
above, but they answer different questions.  :ref:`include-library-names`
defines the translation between them; this document says where the two names
come from.  Both follow the library-name rows of the
:ref:`portable name policy <project-portable-names>`.

A library must declare a ``name``.  A directory that declares none is not a
library, and a ``libraries`` entry pointing at one is an error.  The reason is
that the identity has nowhere else to come from: the apparent name is local to
whoever wrote it, so taking the canonical name from there would let two projects
that had independently chosen one word for different libraries be unable to be
used together.

A library is declared as an object so that kinds other than ``path`` can be
added later.  ``path`` is the only kind defined here.  As everywhere else in the
manifest, a loader ignores a key it does not recognize.

``path`` is a relative POSIX path, resolved against the project root, and it
must resolve *outside* it.  A library is a separate project, not a directory
within one: it has its own root, its own manifest if it has one at all, and its
own file set.  A path that resolves inside the referencing project root is an
error, as is one naming a directory that does not exist.

The library is then loaded exactly as any project is.  Its manifest supplies its
file set when it has one, and the default walk applies when it does not.  Its
files take canonical names under ``@name/``, where *name* is the ``name`` the
library declared.  A source unit reaches it by writing the apparent name its own
project declared:

.. code-block:: c
   :caption: Using a library

   OPENQASM 3.0;
   include "@vendor/gates.inc";

Because :ref:`a library bounds resolution <include-candidates>`, a source unit
inside ``@vendor`` resolves its own targets within ``@vendor``.  It cannot reach
a file of the using project that happens to share a base name, and adding a file
to the library cannot change what the using project resolves.  That isolation is
the reason to depend on a library rather than to copy its files in.

Libraries of libraries
~~~~~~~~~~~~~~~~~~~~~~

A library may declare libraries of its own, and they are loaded in the same way.
Apparent names are local to the project that declares them, so a library's
choices are its own; canonical library names are shared by the whole load,
because a canonical name identifies a source unit throughout one program.

Two arrangements are ordinary:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Arrangement
     - Result
   * - Two projects each write ``c`` for a different library
     - Both load.  Each ``c`` is translated through the map of the project that
       wrote it, so the two never meet.
   * - One library is reached under two apparent names, whether by one project
       or by several
     - It is loaded once, under the one canonical name it declared.

One arrangement remains an error, and it is a genuine collision rather than a
naming accident:

* Two different library root directories that each declare the same ``name``
  is an error.
  Their files would take the same canonical names, and a canonical name
  identifies one source unit.  Nothing here makes canonical library names
  globally unique; uniqueness is conventional, as it is for a package name in
  any registry-free ecosystem, and a collision is diagnosed rather than resolved.

A declaration that names a project already being loaded closes a cycle and is an
error.

The roots taking part in one load are disjoint directory trees.  No root may
contain, or be contained by, any other root of the same load, and that is tested
against every root already bound rather than only against the project that
declares it.  A root inside another root would put one file inside two projects,
and its source units would then be loaded under two canonical names: once as a
file of the outer project and once as a file of the inner one.  Two canonical
names are two source units, so the same gate definition would be incorporated
twice.  Sibling projects in one repository are not affected; they do not contain
one another.

Strict visibility follows from apparent names being local.  A project reaches
only the libraries it declared.  A library that this project depends on may
depend on others, and those are loaded, but this project cannot write a target
that reaches them: it has no apparent name for them, and its own map is the only
one consulted for a target it writes.  Compiling against a library one never
declared is how a dependency becomes load-bearing without anyone deciding it
should.

A library's own ``programs`` field describes that library, not the project using
it.  A project's ``programs`` names only its own files; a library file is not a
program of the project that depends on it.

Manifests absent
~~~~~~~~~~~~~~~~

A project without a manifest and a library without one are treated differently,
and the asymmetry is deliberate:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Case
     - Result
   * - The file being compiled has no discoverable manifest
     - :ref:`Single-file mode <project-discovery>`.  The file is compiled, in a
       synthetic one-file project rooted at its directory.
   * - A ``libraries`` entry points at a directory with no manifest, or with one
       that declares no ``name``
     - An error.  The directory is not a library.

A compilation target arrives with its own identity: a host was handed that file,
and its canonical name is its base name.  A library arrives with none.  Nothing
about the directory says what its files should be called, and the project using
it cannot supply the answer without making that answer local to itself.  Refusing
is what keeps the same library the same library in every project that uses it.

.. _project-programs:

Programs
--------

The file set says which source units belong to the project.  It does not say
which of them are meant to be compiled.  ``programs`` says that: each entry is a
project-relative source name, written exactly as a ``files`` entry is, and must
be the canonical name of a source unit the project offers as a root.  That
source unit becomes the
:ref:`root source unit <include-resolution>` when a host selects it for one
compilation.

An entry that names nothing in the file set is an error rather than something to
ignore.  The order written is the order meant, and two entries that produce the
same canonical name are an error.  Repeating a canonical name would create the
same compilation context, analysis, and diagnostics twice without identifying
a different program.

An empty array is a statement rather than an omission: the project offers
nothing for compilation.  A library of gate definitions is a common example.

When ``programs`` is absent a host derives the set.  Working from the file set,
and resolving each include target the way the section above resolves one rather
than by matching the target text, a host builds the graph of which source unit
includes which, and takes as programs those source units that no other source
unit in the project includes.  Two things are not inclusions for this purpose:
the reserved standard-library name, which resolves outside the project, and an
inclusion written in a source unit outside the project.  A source unit that
only something outside the project includes is not a program, because compiling
it alone loses everything its includer had established, and that is the failure
deriving programs exists to avoid.

A target whose candidates name more than one source unit contributes an edge to
each.  The derivation records reachability; it does not diagnose ambiguity the
way resolution does.

A host must resolve each target, not match its text.  A target is
turned into candidate canonical names, one of which carries the including unit's
name prefix, so a host that matches target text derives the wrong edges whenever
two source units share a base name, and derives no edge at all for a target
written in the ``//`` form or naming a library.

When the derivation names nothing, every source unit is included by another,
which is what a cycle of inclusions produces.  A host then takes every source
unit in the file set as a program.  Two hosts must derive the same set from the
same project.

The derivation is a heuristic, and it is wrong in ordinary cases rather than
only in strange ones.  A library in which no source unit includes another
derives every source unit as a program, which is the opposite of what its author
meant; ``"programs": []`` is how the author says so.  A project with one program
and several helpers that nothing yet includes derives all of them.
``programs`` exists to be right where a derivation
is wrong.  A host manages without it; a project that declares it stops
depending on a guess.

Nothing here obliges an implementation.  The key records what the project
intends, and an implementation still learns its root source unit by being handed
one.


.. _project-stability:

What a project does not change
------------------------------

A manifest never changes what an include target *means*.  It can change which
source units are available, which is what listing ``files`` is for, but it
cannot make one target resolve to a different source unit.  Every way it could
have done so is prevented by a rule above:

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Possibility
     - Why it does not arise
   * - A project supplies its own ``stdgates.inc``
     - Diagnosed as an error, since it could never be reached.  Compiling that
       file directly is unaffected, because nothing resolved a target to reach
       it.
   * - The same file is reached through two roots and incorporated twice
     - The roots of one load are disjoint trees, checked against every root
       already bound.
   * - One name resolves differently depending on the order of roots
     - A canonical name identifies one source unit for the whole load, and two
       roots claiming one library name is an error.
   * - A library a project never declared becomes reachable from it
     - An apparent name is translated through the map of the project that wrote
       it, and a project's map names only the libraries it declared.
   * - A file opened on its own is captured by a distant manifest
     - The upward search stops at a repository, home, or workspace boundary,
       or after 64 directories.
   * - A link escapes the project root
     - Containment is checked against the resolved path before a file is read.
   * - A name means one file on one volume and two on another
     - A case-only source-name collision and every normalization-equivalent
       collision in :ref:`its defined scope <project-portable-names>` is an
       error.
   * - A directory name silently makes its contents a library
     - A project-relative name may not have a component beginning with ``@``.
       Only a ``libraries`` declaration mints a library canonical name.

When a manifest lists its files explicitly, a file that is not listed is not
part of the compilation; that is the purpose of listing them.

A bare target names both a source unit beside the
includer and one at the project root, and neither outranks the other, so giving
two source units the same base name makes such a target ambiguous.  If
``lib/main.qasm`` writes ``include "helper.inc";`` while both ``lib/helper.inc``
and ``helper.inc`` exist, the include is diagnosed rather than silently bound to
one of them.  Adding ``lib/helper.inc`` to a project therefore cannot quietly
change which source unit ``lib/main.qasm`` includes.  An author says which one is
meant by writing the target from the root of the includer's library, as
``//lib/helper.inc`` or ``//helper.inc``.

Reaching a source unit outside the includer's own directory uses the same
naming.  ``..`` is rejected as an include target, so a file in a subdirectory
reaches the project root, or a sibling directory, by writing the target as it
is named from the project root; the includer-prefixed candidate simply names
nothing.  Because :ref:`resolution is implementation defined <include-resolution>`, this
is a property of the arrangement described here rather than a guarantee the
language makes.


.. _project-editing:

Projects under editing
----------------------

Resolution is required to be stable within a single compilation, and is
deliberately not required to be stable between compilations.  That is what makes
a language service possible.  A host that watches a project should treat the
following as changes to the file set:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Change
     - Effect
   * - A manifest appears
     - Re-run discovery.  A file previously compiled on its own may now belong
       to a project.
   * - A manifest is edited and saved
     - Reload it and rebuild the file set.
   * - A manifest is edited but not saved
     - A host with access to the editor's buffer should prefer the buffer, since
       the buffer, not the file, is what the author is working on.
   * - A manifest is removed
     - Re-run discovery, then fall back to single-file mode.
   * - A file appears or is removed
     - With ``files`` present, nothing changes until the manifest changes.
       Otherwise, re-run the walk.
   * - A file is renamed
     - Treat it as a removal and an appearance.
   * - The set of workspace roots changes
     - Re-run discovery, since a stop condition moved.

A source unit that a host holds only in memory, such as an unsaved buffer, an
untitled document, or a notebook cell, has no location relative to a project
root.  Its canonical name is whatever the host chooses, and this document does
not define one.


.. _project-diagnostics:

Diagnostics
-----------

A fault in a project-relative source name — an invalid name, a duplicate, a
collision under case or Unicode normalization, or the reserved name — is
decided across that project's whole declared file set before any of its files
is opened.  A volume that collapses two names into one file would otherwise
decide which of two faults a project has by whether the file happened to open,
and two hosts would disagree about a project neither can load.

Apparent library names are checked across one ``libraries`` object before any
of its declared roots is inspected.  Canonical library-name collisions are
checked as library manifests are bound and remain errors when the libraries
have empty file sets.

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Condition
     - Severity
   * - The manifest is not valid JSON, or its top-level value is not an object
     - Error
   * - The manifest breaks a format restriction: a byte-order mark, a duplicate
       key within one object, or ``NaN``, ``Infinity`` or ``-Infinity``
     - Error
   * - A value anywhere in the manifest is an integer of greater magnitude than
       2\ :sup:`53`\ -1, whether or not the loader recognizes the key holding it
     - Error
   * - An unrecognized key
     - Ignored
   * - A ``files`` entry is not a valid relative name
     - Error
   * - A ``files`` entry names a file that does not exist
     - Error
   * - A ``programs`` entry is not a valid relative name
     - Error
   * - A ``programs`` entry is not a member of the file set
     - Error
   * - A project-relative source name occurs more than once in ``programs``
     - Error
   * - Two canonical names are equal, or differ only by ASCII case
     - Error
   * - Two project-defined names are NFC-equivalent within the collision scope
       in :ref:`project-portable-names`
     - Error
   * - A canonical name is the reserved standard-library name, and is not the
       name of the file being compiled
     - Error
   * - A project-relative source name has a component beginning with ``@``
     - Error
   * - A ``libraries`` declaration is malformed, or names an unusable library
       name or a path that is not a relative POSIX path
     - Error
   * - A declared library's root directory does not exist
     - Error
   * - A declared library's root directory contains, or is contained by, another root of
       the same load
     - Error
   * - A declared library declares no ``name``, or has no manifest
     - Error
   * - Two different library root directories declare the same ``name``
     - Error
   * - A library declaration closes a cycle back to a project already loading
     - Error
   * - A file lies outside the root that supplies it
     - Error
   * - An include target is not a portable name
     - Error

A diagnostic about the manifest is reported against the manifest, and a
diagnostic about an include target is reported against the ``include``
statement.  A host that can express a relationship between the two should point
the include-target diagnostic at the manifest, since that is where the file set
is declared.

Standard-library JSON parsers report a location for a syntax error and not for
a value that parsed successfully, so a host built on one reports manifest
diagnostics against the file rather than against the offending entry.


.. _project-schema:

Schema and editor support
-------------------------

A JSON Schema for the manifest is published at
``https://openqasm.com/_static/schemas/openqasm-project-v1.schema.json``.  It
describes the fields above and deliberately does not forbid unrecognized keys,
matching the rule that a loader ignores them rather than rejecting them.

An editor associates the schema with the manifest in one of two ways.

The manifest names the schema
   Setting ``$schema`` to the published URL is enough for editors that resolve
   it.  Because that requires fetching over the network, and some editors let a
   user disable remote schema fetching, this is the more convenient option
   rather than the more reliable one.

An extension associates the schema
   An editor extension can bind a schema to a file name, which needs no network
   access and works when a user has disabled remote fetching.  In Visual Studio
   Code this is a ``jsonValidation`` contribution matching ``openqasm.json``.
   Shipping a copy of the schema inside the extension is preferable to pointing
   at the published URL, for the same reason.

Editors do not generally associate a schema with a file name on their own.  An
editor that consumes a public schema catalog may do so once the schema is
registered there, but Visual Studio Code does not use such a catalog, so an
extension or an in-file ``$schema`` key is required there.
