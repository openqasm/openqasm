"""Generate a project manifest from a directory tree.

A project manifest is written by hand.  This module exists because two of the things it
declares can be read off the tree instead: the file set, and which of those files are
offered for compilation.  A third, the ``name`` a project is known by when another project
uses it as a library, cannot be inferred and is supplied by the caller.

Nothing here is normative, and no host is required to use it.  The project profile at
https://openqasm.com/project.html defines what a manifest means; this only saves writing
one out.

The module sits between :mod:`openqasm3.project`, which reads the file system and needs no
parser, and :mod:`openqasm3.parser`, which parses and reads no files.  Generating a manifest
needs both, and putting it in either would have cost that module the separation that makes
it useful on its own.

Importing this module imports the parser, so, like :mod:`openqasm3.project`, it is not
imported by ``import openqasm3``.

It can also be run directly, which writes the manifest to standard output and any
undeclared library names to standard error::

    python -m openqasm3.manifest /work/proj --name vendor --programs

It never writes a file.  Redirecting the output is the caller's decision, so that
generating a manifest cannot overwrite one that was written by hand.

.. currentmodule:: openqasm3.manifest

.. autofunction:: generate_manifest

.. autoclass:: GeneratedManifest
   :members:
"""

__all__ = [
    "GeneratedManifest",
    "generate_manifest",
]

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence, Tuple

from .parser import _include_targets, derive_programs
from .project import (
    MANIFEST_NAME,
    FileSetError,
    Manifest,
    PathLike,
    collect_default_file_set,
    load_project,
    read_manifest,
)
from .resolver import LIBRARY_PREFIX, STANDARD_LIBRARY_NAME, library_name


@dataclass
class GeneratedManifest:
    """A generated manifest, and the one thing generating it cannot settle."""

    manifest: Manifest
    """The manifest, ready to be serialized as JSON.  A caller writes it; this module never
    does, so that generating one is never destructive."""

    undeclared_libraries: Tuple[str, ...] = ()
    """Library names the tree's include targets reach that the manifest does not declare,
    sorted.  They are reported rather than declared because only the caller knows where each
    library lives, and a guessed path would be worse than an absent one: it would produce a
    manifest that looks complete and does not load."""


def _referenced_libraries(sources: Mapping[str, str]) -> Tuple[str, ...]:
    """The library names the root project's include targets reach, sorted."""
    referenced = set()
    for name in sources:
        if name.startswith(LIBRARY_PREFIX):
            continue
        for target in _include_targets(sources[name], includer=name):
            if target != STANDARD_LIBRARY_NAME and target.startswith(LIBRARY_PREFIX):
                referenced.add(library_name(target))
    return tuple(sorted(referenced))


def generate_manifest(
    root: PathLike,
    *,
    name: Optional[str] = None,
    explicit_files: bool = False,
    programs: bool = False,
) -> GeneratedManifest:
    """Generate a manifest describing the project rooted at ``root``.

    :param root: The project root.  Its files are collected by the same default walk a
        loader applies to a manifest with no ``files`` key, so a generated manifest
        describes the tree a loader would have found anyway.
    :param name: The canonical name to declare, for a project meant to be used as a library.
        When ``None`` a name already declared at ``root`` is kept, and a project that
        declares none stays without one, which is right for one used only on its own.  It is a
        parameter rather than something taken from the directory name, because a library's
        identity should not change when its checkout is renamed.
    :param explicit_files: Emit a ``files`` key listing the walk's result, rather than
        leaving the key out and letting the walk supply the same set.  Listing them fixes
        the set against later additions to the tree; leaving them out keeps the manifest
        short and lets the tree stay the source of truth.
    :param programs: Emit a ``programs`` key derived from the include graph, through
        :func:`openqasm3.derive_programs`.  Left out when ``False``, which means a
        host derives the same set for itself.  The derivation is a heuristic, and writing it
        down is worthwhile precisely because it can then be corrected by hand.
    :return: The manifest, and the library references it could not resolve into declarations.
    :raises QASM3ParsingError: A file in the tree could not be parsed.  Every file is parsed,
        whichever options are set, because that is how a library reference is found.
    :raises ProjectError: The tree could not be read, the supplied ``name`` is invalid, or a
        recognized field in the completed manifest is malformed or unsupported.

    Generation grammar-parses every file to extract and validate include targets.  It does
    not apply supported-version or feature-version rules, so a generated manifest does not
    certify that the sources can be compiled.  Normal :func:`openqasm3.parse` applies those
    version checks in a compilation context.

    An existing manifest at ``root`` is read and every key it holds is carried through,
    except ``files`` and ``programs``, which this function derives.  A manifest is an open
    object, so keeping only the keys understood here would silently edit out ``$schema``,
    ``$comment``, and anything a later version defines.  An explicit ``name`` argument
    overrides a declared one; otherwise a declared ``name`` is kept, because discarding it
    would rename every canonical name the library's consumers had written.

    Before returning, the completed mapping's recognized fields pass the same semantic
    validation used by :func:`openqasm3.project.load_project`.  Unrecognized top-level and
    nested values are preserved unchanged and are not assigned semantics by this generator.
    """
    base = os.fspath(root)
    try:
        entries = collect_default_file_set(base)
    except OSError as exc:
        raise FileSetError("could not read project tree %r: %s" % (base, exc)) from exc
    manifest_path = os.path.join(base, MANIFEST_NAME)
    existing: Manifest = read_manifest(manifest_path) if os.path.isfile(manifest_path) else {}

    # Start from what the author wrote, so that a key this generator does not derive --
    # "$schema", "$comment", "libraries", or one from a later version -- survives.
    manifest = existing.copy()
    manifest.pop("files", None)
    manifest.pop("programs", None)
    if name is not None:
        manifest["name"] = name
    elif "name" not in existing:
        manifest.pop("name", None)

    candidate_manifest = manifest.copy()
    candidate_manifest["files"] = list(entries)
    candidate = load_project(base, manifest=candidate_manifest)

    if explicit_files:
        manifest["files"] = list(entries)
    if programs:
        manifest["programs"] = list(derive_programs(candidate))

    loaded = load_project(base, manifest=manifest)
    undeclared = tuple(
        reference
        for reference in _referenced_libraries(loaded.sources)
        if reference not in loaded.library_bindings[""]
    )
    return GeneratedManifest(manifest=manifest, undeclared_libraries=undeclared)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Write a generated manifest to standard output."""
    parser = argparse.ArgumentParser(description="Generate an OpenQASM project manifest.")
    parser.add_argument("root", help="the project root to describe")
    parser.add_argument("--name", help="the name to declare, for a project used as a library")
    parser.add_argument(
        "--explicit-files",
        action="store_true",
        help="list the file set rather than leaving it to the default walk",
    )
    parser.add_argument(
        "--programs", action="store_true", help="derive the programs from the include graph"
    )
    arguments = parser.parse_args(argv)

    generated = generate_manifest(
        arguments.root,
        name=arguments.name,
        explicit_files=arguments.explicit_files,
        programs=arguments.programs,
    )
    print(json.dumps(generated.manifest, indent=2))
    for reference in generated.undeclared_libraries:
        print(
            "warning: '%s' is included but not declared in 'libraries'; add it with the"
            " path to that library's root" % reference,
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
