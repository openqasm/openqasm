..
    Each module docstring manually exports its symbols with autodoc directives,
    so "members" is not set here.

.. automodule:: openqasm3.resolver

.. automodule:: openqasm3.filesystem

.. automodule:: openqasm3.project

.. automodule:: openqasm3.manifest


.. _load-behaviors:

Parser inputs
=============

``include`` statements are not resolved by default, and :func:`openqasm3.parse`
performs no file-system access unless you supply a resolver that performs it.
Resolution is enabled by passing ``includes=`` to :func:`openqasm3.parse`.
Supply a complete :class:`~openqasm3.resolver.IncludeEnvironment`, or use a
mapping, callable, or :class:`~openqasm3.resolver.IncludeResolver` as a
convenience source backend.  The three raw backend forms are normalized through
:meth:`~openqasm3.resolver.IncludeEnvironment.unscoped`, so apparent library
names remain canonical as written.

Pass ``name=`` alongside ``includes=`` to give the parsed source its canonical
source identity.  This is the identity that include targets are resolved with
respect to.  It defaults to ``"<input>"``, which has no name prefix.  Identities
are nonempty strings owned by their resolver: the parser compares them exactly
but does not require a path, URI, or portable logical-name scheme.


1. No environment
-----------------

The default.  ``include`` statements are parsed and retained, but no included
source is loaded, and :attr:`~openqasm3.ast.Include.canonical_name` stays
``None``.  The source passed to the parser is still recorded at index 0 of
:attr:`~openqasm3.ast.Program.sources`, so every :class:`~openqasm3.ast.Span`
has valid source provenance.  This is the right choice for a tool that only
parses or formats one source unit.
Include targets are still validated, so a target that is empty, absolute,
drive-qualified, or that contains a ``.``, ``..`` or ``\`` component is rejected
even though no source is loaded.

.. code-block:: python

    import openqasm3

    program = openqasm3.parse('OPENQASM 3.0; include "stdgates.inc";')
    assert program.statements[0].canonical_name is None
    assert [unit.canonical_name for unit in program.sources] == ["<input>"]


2. A mapping
------------

A mapping from canonical name to source text.  This suits notebooks, test
harnesses, virtual file systems, and language servers holding unsaved buffers::

   import openqasm3

   sources = {
       "mylib.inc": 'gate flip q { U(pi, 0, pi) q; }',
   }
   program = openqasm3.parse(
       'OPENQASM 3.0; include "mylib.inc";',
       includes=sources,
       name="main.qasm",
   )
   assert [unit.canonical_name for unit in program.sources] == [
       "main.qasm",
       "mylib.inc",
   ]

When an exact key is absent, :class:`~openqasm3.resolver.DictResolver` compares
keys under Unicode Normalization Form C.  An exact key always wins.  If more
than one distinct key is equivalent to a non-exact lookup,
:class:`~openqasm3.resolver.AmbiguousIncludeTargetError` is raised rather than
selecting a key according to mapping order.


3. A callable
-------------

A function taking one canonical name.  The environment forms the candidate
canonical names for an include target before calling you, so a callable never
has to implement the naming rules itself.

Return ``None`` to indicate that you do not supply that source unit, a bare
string to supply its source text, or a ``(source, canonical_name)`` pair when
you unify several spellings onto one source unit.  The returned identity may
use any nonempty string convention your resolver owns::

   import openqasm3

   def resolve(canonical_name):
       if canonical_name == "mylib.inc":
           return "gate flip q { U(pi, 0, pi) q; }"
       return None

   program = openqasm3.parse('OPENQASM 3.0; include "mylib.inc";', includes=resolve)

Raise an :class:`~openqasm3.resolver.IncludeError` rather than returning
``None`` when you do supply a source unit but cannot load it, so that a real
failure is not mistaken for a miss.  During one parse, the same target from the
same source unit must resolve consistently, and a canonical name must identify
one source text.  The parser raises
:class:`~openqasm3.resolver.IncludeError` if a resolver produces inconsistent
results, and :class:`~openqasm3.resolver.AmbiguousIncludeTargetError` if an
include target matches more than one source unit.


4. A resolver object
--------------------

An :class:`~openqasm3.resolver.IncludeResolver` instance.  Use this when you
need composition, or when your resolution logic carries state::

   import openqasm3
   from openqasm3.filesystem import FileSystemResolver

   source = 'OPENQASM 3.0; include "mylib.inc";'
   resolver = openqasm3.ChoiceResolver([
       openqasm3.DictResolver({"mylib.inc": "gate flip q { U(pi, 0, pi) q; }"}),
       FileSystemResolver(["./lib"]),
   ])
   program = openqasm3.parse(source, includes=resolver, name="main.qasm")

:class:`~openqasm3.resolver.ChoiceResolver` consults each resolver in order and
takes the first that does not return ``None``.


5. An include environment
-------------------------

An :class:`~openqasm3.resolver.IncludeEnvironment` binds a source backend to
the name-visibility rules governing every lookup.  Construct one explicitly
when resolution policy is passed between components, or when library names are
scoped.  The unscoped form accepts the same mapping, callable, and resolver
backends as the convenience forms above::

    import openqasm3
    from openqasm3.filesystem import FileSystemResolver

    source = 'OPENQASM 3.0; include "mylib.inc";'
    backend = openqasm3.ChoiceResolver([
        openqasm3.DictResolver({"mylib.inc": "gate flip q { U(pi, 0, pi) q; }"}),
        FileSystemResolver(["./lib"]),
    ])
    environment = openqasm3.IncludeEnvironment.unscoped(backend)
    program = openqasm3.parse(source, includes=environment, name="main.qasm")

The parser uses an environment directly.  It does not extract or accept a
second visibility argument that could describe a different resolution world.


Scoped library names
====================

A resolver is always asked for canonical names.  A target such as
``@vendor/gates.inc`` names a library by its *apparent* name, which is chosen by
whoever wrote the source unit that uses it.  The environment translates that
name into a canonical library name *before* consulting its resolver.  A
resolver therefore never implements the translation, and a
:class:`~openqasm3.resolver.DictResolver` is always keyed by canonical names.

An unscoped environment performs no translation: every apparent library name
is canonical as written.  This suits a host with one flat source table whose
keys are exactly the targets its programs write.

Use :meth:`~openqasm3.resolver.IncludeEnvironment.scoped` when apparent library
names are local to their owners.  The outer mapping is keyed by canonical
library name, or ``""`` for the program itself.  Each inner mapping translates
that owner's apparent names into canonical library names::

   import openqasm3

   libraries = {
       "@vendor/gates.inc": 'include "@h/helpers.inc";',
       "@helpers/helpers.inc": "gate flip q { U(pi, 0, pi) q; }",
   }
   bindings = {"": {"v": "vendor"}, "vendor": {"h": "helpers"}}
   environment = openqasm3.IncludeEnvironment.scoped(
       openqasm3.DictResolver(libraries),
       bindings,
   )
   program = openqasm3.parse(
       'OPENQASM 3.0; include "@v/gates.inc";',
       includes=environment,
       name="main.qasm",
   )

Every non-root outer key and both names in each inner mapping are bare library
names.  :func:`~openqasm3.resolver.validate_library_name` rejects empty names,
path separators, a leading ``@``, ``.`` and ``..``, and the pattern characters
``*`` and ``?``.  Square and curly brackets are ordinary name characters.

The scoped constructor validates and copies both mapping levels, then retains
read-only views.  Mutating ``bindings`` or one of its inner mappings afterward
does not change candidate formation or resolution.

Scoped visibility is strict.  The program above reaches ``@vendor/`` because
its own bindings name it, but it cannot reach ``@helpers/`` even though
``@vendor/`` can.  A library's own libraries are not inherited by its users.
An empty scoped environment intentionally makes no apparent library available::

   closed = openqasm3.IncludeEnvironment.scoped({}, {})
   assert closed.candidates("@vendor/gates.inc", "main.qasm") == ()

This differs from an unscoped environment, where the same target remains
``"@vendor/gates.inc"``.  A missing binding yields no candidate and is reported
as an unresolved target rather than an invalid target.

The mapping example holds sources in memory.  To load libraries from disk,
use :class:`openqasm3.filesystem.LibraryResolver`, which maps canonical library
roots lazily and keeps the ``@name/`` canonical name as each source unit's
identity::

   from openqasm3.filesystem import FileSystemResolver, LibraryResolver

   backend = openqasm3.ChoiceResolver([
       LibraryResolver({
           "vendor": "/path/to/vendor",
           "helpers": "/path/to/helpers",
       }),
       FileSystemResolver(["/path/to/program"]),
   ])
   environment = openqasm3.IncludeEnvironment.scoped(backend, bindings)
   program = openqasm3.parse(
       'OPENQASM 3.0; include "@v/gates.inc";',
       includes=environment,
       name="main.qasm",
   )

The backend can supply every configured canonical library, while environment
bindings decide which source owner can ask for each one.  The two filesystem
resolvers divide the work rather than competing: resolved paths identify a
program's own files, and canonical names identify a library's.


File-system source identities
=============================

:class:`openqasm3.filesystem.FileSystemResolver` resolves candidates against
explicit search roots.  A candidate is accepted only if the resolved path of
the file that would be opened is inside the matching root, so symbolic links
cannot escape the configured search path.  The source unit's canonical name is
the absolute resolved file path, written with forward slashes.  This is an
opaque identity convention owned by this resolver, not a grammar imposed on
other resolvers.

Because the identity is the path as the caller spelled it, apart from symbolic
links, two names that reach one file are two source units.  That happens across
search roots, through a hard link, and, on a volume that ignores the
difference, through case or Unicode normalization alone.  Each is incorporated
separately, so a declaration they share is declared more than once.

Using the resolved path as the canonical name also preserves root provenance for
nested includes.  If two search roots contain similar relative layouts and a
parent source unit is found in the second root, a later ``include`` inside that
parent resolves relative to the second root rather than drifting back to an
earlier root.

Once a file is selected, failures to open or decode it are reported as
:class:`~openqasm3.resolver.IncludeError`.  A missing file or a path outside
the configured roots remains a resolver miss, allowing another resolver in a
:class:`~openqasm3.resolver.ChoiceResolver` to supply it.

By contrast, :mod:`openqasm3.project` assigns validated project-relative source
names as canonical names, unchanged.  Both conventions satisfy the
same resolver contract; they choose different identity strings for different
host requirements.


The standard library
====================

When ``includes=`` enables resolution, the environment resolves the exact target
``"stdgates.inc"`` before its caller-supplied backend.  The parser records an
empty source unit whose canonical name is ``"stdgates.inc"``; it neither ships
nor parses standard-gate declarations.  This preserves include provenance and
incorporation-once behavior without making the AST parser a standard-library
implementation.

The OpenQASM specification defines the standard library.  Downstream compiler
tooling is responsible for resolving standard-gate symbols, type checking their
uses, and selecting language-version-specific implementations.  The root
program's :attr:`~openqasm3.ast.Program.effective_version` governs this one
program-wide selection, including when ``stdgates.inc`` is first included by a
nested source with a different declared version.  The synthetic source unit's
:attr:`~openqasm3.ast.SourceUnit.effective_version` records the same value.  All
other include targets remain the caller resolver's responsibility.


Working with a resolved program
===============================

A source unit is incorporated into a program at most once per canonical name,
so a library included from two places contributes its declarations only once.
Resolved statements are held on :class:`~openqasm3.ast.SourceUnit` objects in
:attr:`~openqasm3.ast.Program.sources`, and each :class:`~openqasm3.ast.Include`
records the index of the unit it resolved to.

``Program.version`` and :attr:`~openqasm3.ast.SourceUnit.version` retain only
explicit header values.
Their ``effective_version`` fields record the normalized version used to parse
the corresponding source, including root defaults and inherited values.  The
root effective version is preserved by
:func:`~openqasm3.resolver.flatten_includes`.

Version-support and declaration failures expose stable machine-readable codes
through :attr:`openqasm3.parser.QASM3ParsingError.identity`.  In particular,
an included source whose declared version exceeds the root reports
``"include-version-exceeds-root"``.  Parsing errors without an agreed identity
leave the attribute ``None``, so callers should test for the codes they handle
rather than assuming every parsing error has one.

Source units are deliberately not AST nodes, so enabling resolution does not
change what an existing :class:`~openqasm3.visitor.QASMVisitor` traverses.  Call
:func:`~openqasm3.resolver.flatten_includes` when you want the spliced view::

   flattened = openqasm3.flatten_includes(program)

Printing is unaffected by resolution.  :func:`openqasm3.dumps` emits the
``include`` statement and never the source it resolved to, so a program
round-trips identically whether or not includes were resolved.


Loading a project
=================

:mod:`openqasm3.project` builds an immutable :class:`~openqasm3.project.LoadedProject`
snapshot from a directory.  Its :attr:`~openqasm3.project.LoadedProject.sources`
and :attr:`~openqasm3.project.LoadedProject.library_bindings` are read-only
mappings, and its :attr:`~openqasm3.project.LoadedProject.environment` binds
those exact snapshots into one resolution context.  Mutating dictionaries used
to construct the project afterward cannot change what it resolves.

Use :func:`openqasm3.parse_project` to parse from that coherent context::

    import openqasm3
    from openqasm3.project import load_target

    loaded = load_target("/work/proj/main.qasm")
    program = openqasm3.parse_project(loaded)

An explicit source name overrides the loaded compilation root.  If neither is
available, or if the selected name is absent from ``sources``,
:func:`~openqasm3.parse_project` raises :class:`ValueError` before parsing.
Project loading itself remains parser-independent and can be used without the
``[parser]`` extra.

The loaded project is a finite inventory.  Generic resolver backends may be
lazy or infinite and therefore expose no equivalent enumeration operation.
See the specification's non-normative project definition for the loading rules.

Deriving project programs
=========================

:attr:`openqasm3.project.LoadedProject.programs` preserves only the manifest's
declaration.  When it is ``None``, pass the loaded project to
:func:`openqasm3.derive_programs`.  Derivation parses only the project's own
finite source inventory and uses its environment to form every candidate edge;
it does not resolve includes or enumerate a generic resolver.  This explicit
parser-extra step keeps project loading parser-independent.

Generating a manifest
=====================

:mod:`openqasm3.manifest` goes the other way, describing a directory tree as a
new manifest or regenerating an existing one while preserving its declarations
and extension keys.  See that module above.
