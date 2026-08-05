..
   Both module docstrings manually export their symbols so that the four load
   behaviours lead the page, so we don't specify "members" here.

.. automodule:: openqasm3.resolver

.. automodule:: openqasm3.filesystem


.. _load-behaviours:

The four load behaviours
========================

``include`` statements are not resolved by default, and :func:`openqasm3.parse`
performs no file-system access unless you supply a resolver that performs it.
Resolution is enabled by passing ``includes=`` to :func:`openqasm3.parse`, which
accepts any of four forms.  Every form is normalised internally by
:func:`~openqasm3.resolver.as_resolver`, so the four are interchangeable at the
call site.

Pass ``name=`` alongside ``includes=`` to give the parsed source its canonical
name.  This is the name that include targets are resolved with respect to.  It
defaults to ``"<input>"``, which has no name prefix.


1. No resolver
--------------

The default.  ``include`` statements are parsed and retained, but no source is
loaded, and :attr:`~openqasm3.ast.Include.canonical_name` stays ``None``.  This
is the right choice for a tool that only parses or formats one source unit.
Include targets are still validated, so targets containing a ``.`` or ``..``
path component are rejected even though no source is loaded::

   import openqasm3

   program = openqasm3.parse('OPENQASM 3.0; include "stdgates.inc";')
   assert program.statements[0].canonical_name is None
   assert program.sources == []


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


3. A callable
-------------

A function taking the include target and the canonical name of the source unit
that contains the ``include`` statement.  Both arguments matter: without the
includer, a target cannot be resolved with respect to where it was written.

Return ``None`` to indicate that the target is not one you handle, a
``(source, canonical_name)`` pair to resolve it, or a bare string if the target
should also serve as the canonical name::

   import openqasm3

   def resolve(target, includer):
       if target == "mylib.inc":
           return "gate flip q { U(pi, 0, pi) q; }", "mylib.inc"
       return None

   program = openqasm3.parse('include "mylib.inc";', includes=resolve)

Raise an :class:`~openqasm3.resolver.IncludeError` rather than returning
``None`` when you do handle a target but cannot load it, so that a real failure
is not mistaken for a miss.  During one parse, the same target from the same
source unit must resolve consistently, and a canonical name must identify one
source text.  The parser raises :class:`~openqasm3.resolver.IncludeError` if a
resolver produces inconsistent results.


4. A resolver object
--------------------

An :class:`~openqasm3.resolver.IncludeResolver` instance.  Use this when you
need composition, or when your resolution logic carries state::

   import openqasm3
   from openqasm3.filesystem import FileSystemResolver

   resolver = openqasm3.ChoiceResolver([
       openqasm3.DictResolver({"mylib.inc": "gate flip q { U(pi, 0, pi) q; }"}),
       FileSystemResolver(["./lib"]),
   ])
   program = openqasm3.parse(source, includes=resolver, name="main.qasm")

:class:`~openqasm3.resolver.ChoiceResolver` consults each resolver in order and
takes the first that does not return ``None``.


File-system canonical names
===========================

:class:`openqasm3.filesystem.FileSystemResolver` resolves candidates against
explicit search roots.  A candidate is accepted only if the resolved path of
the file that would be opened is inside the matching root, so symbolic links
cannot escape the configured search path.  The source unit's canonical name is
the resolved file path, written with forward slashes.

Using the resolved path as the canonical name also preserves root provenance for
nested includes.  If two search roots contain similar relative layouts and a
parent source unit is found in the second root, a later ``include`` inside that
parent resolves relative to the second root rather than drifting back to an
earlier root.


The standard library
====================

When ``includes=`` enables resolution, the parser itself resolves the exact
target ``"stdgates.inc"`` before the caller-supplied resolver.  It creates an
empty source unit whose canonical name is ``"stdgates.inc"``; it neither ships
nor parses standard-gate declarations.  This preserves include provenance and
incorporation-once behavior without making the AST parser a standard-library
implementation.

The OpenQASM specification defines the standard library.  Downstream compiler
tooling is responsible for resolving standard-gate symbols, type checking their
uses, and selecting language-version-specific implementations.  All other
include targets remain the caller resolver's responsibility.


Working with a resolved program
===============================

A source unit is incorporated into a program at most once per canonical name,
so a library included from two places contributes its declarations only once.
Resolved statements are held on :class:`~openqasm3.ast.SourceUnit` objects in
:attr:`~openqasm3.ast.Program.sources`, and each :class:`~openqasm3.ast.Include`
records the index of the unit it resolved to.

Source units are deliberately not AST nodes, so enabling resolution does not
change what an existing :class:`~openqasm3.visitor.QASMVisitor` traverses.  Call
:func:`~openqasm3.resolver.flatten_includes` when you want the spliced view::

   flattened = openqasm3.flatten_includes(program)

Printing is unaffected by resolution.  :func:`openqasm3.dumps` emits the
``include`` statement and never the source it resolved to, so a program
round-trips identically whether or not includes were resolved.
