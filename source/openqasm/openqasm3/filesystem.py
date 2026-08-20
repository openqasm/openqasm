"""
==========================================================
File-system include resolution (``openqasm3.filesystem``)
==========================================================

Opt-in :class:`~openqasm3.resolver.IncludeResolver` implementations that load source units
from disk.  :class:`FileSystemResolver` supplies a program's own files and
:class:`LibraryResolver` supplies the source units of named libraries.

This is the only module in the package that touches the file system.  It is never used unless a
caller explicitly constructs one of its resolvers and supplies it as a raw parser backend or as
part of an :class:`~openqasm3.resolver.IncludeEnvironment`, because an include target may originate
from untrusted source text.

.. currentmodule:: openqasm3.filesystem
.. autoclass:: FileSystemResolver
.. autoclass:: LibraryResolver
"""

__all__ = ["FileSystemResolver", "LibraryResolver"]

import os
from typing import Dict, Iterable, List, Mapping, Optional, Union

from .resolver import (
    IncludeError,
    IncludeResolver,
    library_name,
    LIBRARY_PREFIX,
    ResolvedSource,
    validate_library_name,
)


class FileSystemResolver(IncludeResolver):
    """Resolves canonical names against an explicit list of search roots.

    This resolver chooses the absolute resolved file path as its opaque source identity.  A
    library-qualified canonical name is declined rather than resolved because that identity would
    not carry the library prefix, so a library loaded through it would lose its isolation.  A host
    that supplies libraries composes them separately:
    ``ChoiceResolver([LibraryResolver(roots), FileSystemResolver([root])])`` when they are on
    disk, or ``ChoiceResolver([DictResolver(libraries), FileSystemResolver([root])])`` when
    they are already in memory.

    Every resolver is asked for canonical names only.  An apparent library name written in an
    include target is translated into a canonical one by
    :meth:`~openqasm3.resolver.IncludeEnvironment.candidates` *before* any resolver is consulted,
    so the dictionary in that composition is keyed by canonical names and a host composing
    resolvers never implements the translation itself.  An
    :meth:`~openqasm3.resolver.IncludeEnvironment.unscoped` environment treats an apparent name
    as its own canonical name.  A :meth:`~openqasm3.resolver.IncludeEnvironment.scoped`
    environment limits each source owner to its declared bindings.

    :param search_path: Directories to search, in order.  A canonical name is only accepted if the
        file it names lies inside the root being searched, so an include target cannot reach
        outside the roots the caller designated.
    :param encoding: Text encoding used to read source files.

    A candidate is checked after resolving symbolic links, so a file is only accepted if the path
    that would be opened is inside the matching root.  Returned identities are resolved paths
    expressed with forward slashes; resolving symbolic links is the only way the spelling a
    caller asked for is changed.  Two names that reach one file therefore give two identities
    and two source units, whether they differ by search root, by hard link, or, on a volume
    that ignores the difference, only by case or Unicode normalization.  The specification
    makes no promise about physical file identity.
    """

    def __init__(
        self,
        search_path: Iterable[Union[str, "os.PathLike[str]"]],
        *,
        encoding: str = "utf-8",
    ):
        self._search_path: List[str] = [os.path.realpath(os.fspath(root)) for root in search_path]
        if not self._search_path:
            raise ValueError("FileSystemResolver requires at least one search root")
        self._encoding = encoding

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        if canonical_name.startswith(LIBRARY_PREFIX):
            # Resolved paths are this resolver's identity, which would strip the library prefix
            # and silently lose a library's isolation, so library names are declined instead.
            # LibraryResolver supplies them, keeping the canonical name as the identity.
            return None
        for root in self._search_path:
            path = os.path.realpath(os.path.join(root, canonical_name))
            try:
                inside_root = os.path.commonpath([root, path]) == root
            except ValueError:
                # ``commonpath`` raises when paths cannot be compared, such as Windows paths
                # on different drives; that means the candidate is outside this root.
                inside_root = False
            if not inside_root:
                # The candidate escapes the designated root, so this root does not supply it.
                continue
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding=self._encoding) as stream:
                    # The resolved path is the identity, so a nested include stays in the root
                    # its includer was found in rather than searching the roots afresh.
                    return ResolvedSource(stream.read(), path.replace("\\", "/"))
            except (LookupError, OSError, UnicodeError) as exc:
                raise IncludeError(
                    f"could not read '{path}' for source unit '{canonical_name}': {exc}"
                ) from exc
        return None

    def __repr__(self):
        return f"{type(self).__name__}({self._search_path!r})"


class LibraryResolver(IncludeResolver):
    """Resolves library-qualified canonical names against a directory for each library.

    This is the counterpart to :class:`FileSystemResolver`, which declines library names because
    its identities are resolved paths and a path cannot carry the ``@name/`` prefix.  This resolver
    returns the canonical name it was asked for, so a source unit inside a library keeps its
    library and resolves its own targets within it.

    Compose the two to supply a program from one place and its libraries from another.  The keys
    are canonical library names, because a resolver is always asked for canonical names, and
    a scoped environment is what lets a program write a different apparent name::

        environment = IncludeEnvironment.scoped(
            ChoiceResolver(
                [
                    LibraryResolver(
                        {"vendor": "/path/to/vendor", "helpers": "/path/to/helpers"}
                    ),
                    FileSystemResolver(["/path/to/program"]),
                ]
            ),
            {"": {"v": "vendor"}, "vendor": {"h": "helpers"}},
        )
        openqasm3.parse(source, includes=environment, name="main.qasm")

    A program writing ``@v/gates.inc`` reaches ``@vendor/gates.inc``, and ``@vendor`` writing
    ``@h/util.inc`` reaches ``@helpers/util.inc``.  Translation happens in
    :meth:`~openqasm3.resolver.IncludeEnvironment.candidates` before any resolver is consulted,
    so this mapping holds every library that may be reached, keyed by canonical name, while the
    environment bindings decide which of them each source owner sees.  An unscoped environment
    leaves an apparent name as its own canonical name.

    :param roots: Canonical library name to the directory holding that library's source units.  A
        name this mapping does not hold is declined, so another resolver may supply it.
    :param encoding: Text encoding used to read source files.

    A candidate is checked after resolving symbolic links, so a file is only accepted if the path
    that would be opened is inside that library's own root.
    """

    def __init__(
        self,
        roots: Mapping[str, Union[str, "os.PathLike[str]"]],
        *,
        encoding: str = "utf-8",
    ):
        self._roots: Dict[str, str] = {
            validate_library_name(name): os.path.realpath(os.fspath(root))
            for name, root in roots.items()
        }
        self._encoding = encoding

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        if not canonical_name.startswith(LIBRARY_PREFIX):
            return None
        name = library_name(canonical_name)
        root = self._roots.get(name)
        if root is None:
            return None
        relative = canonical_name[len(LIBRARY_PREFIX) + len(name) + 1 :]
        path = os.path.realpath(os.path.join(root, relative))
        try:
            inside_root = os.path.commonpath([root, path]) == root
        except ValueError:
            # ``commonpath`` raises when paths cannot be compared, such as Windows paths on
            # different drives; that means the candidate is outside this library.
            inside_root = False
        if not inside_root or not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding=self._encoding) as stream:
                # The canonical name is the identity, so the library keeps its isolation.
                return ResolvedSource(stream.read(), canonical_name)
        except (LookupError, OSError, UnicodeError) as exc:
            raise IncludeError(
                f"could not read '{path}' for source unit '{canonical_name}': {exc}"
            ) from exc

    def __repr__(self):
        return f"{type(self).__name__}({self._roots!r})"
