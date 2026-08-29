"""
=======================================
Project loading (``openqasm3.project``)
=======================================

Turns a directory of OpenQASM source files into an immutable
:class:`LoadedProject`.  Its :attr:`LoadedProject.environment` binds the finite
source snapshot to its owner-local library names for parsing.

A *project* is a directory containing an ``openqasm.json`` manifest that declares
which files take part in a compilation.  The manifest makes a host's inputs
explicit; it changes nothing about how an ``include`` statement is resolved, and
a source file compiled without one behaves exactly as it did before.

When no project is found for a specific source file, the fallback is
single-file mode: the file's containing directory is treated as a synthetic
project root, the file set is exactly that one file, and its canonical name is
its basename.  This fallback is evaluated per compilation target and never
extends to sibling files or to a broader host-global project policy; a host must
not infer a project from nearby directories while evaluating that fallback.

Like :mod:`openqasm3.filesystem`, this module reads the file system, so it is
never imported unless a caller asks for it.  A manifest may declare which of
its files are meant to be compiled, which is a question the language leaves to
whoever invokes the parser.  When it does, :attr:`LoadedProject.programs`
reports the declaration, so a caller need not be told what to compile::

    import openqasm3
    from openqasm3.project import load_project, load_target

    loaded = load_target("/work/proj/programs/main.qasm")
    program = openqasm3.parse_project(loaded)

    loaded = load_project("/work/proj")
    selected = (
        openqasm3.derive_programs(loaded)
        if loaded.programs is None
        else loaded.programs
    )
    programs = [openqasm3.parse_project(loaded, name) for name in selected]

Because ``sources`` is a mapping, the parser resolves relative include targets
against the canonical name of the including source unit, and continues to
resolve the reserved standard-library name ahead of anything supplied here.

:attr:`LoadedProject.programs` is ``None`` when the manifest declared no
``programs`` key, which is not the same as an empty tuple.  Deriving the set from
the include graph in that case needs a parser, so it lives in
``openqasm3.parser.derive_programs`` rather than here: this module reads the file
system but never parses, which is what lets a project holding one unparseable
file load at all.

:attr:`LoadedProject.environment` keeps source lookup and library bindings in one
immutable resolution context.  The name a source unit writes for a library is
local to the project that declared it, and :attr:`LoadedProject.library_bindings`
translates it into the canonical name the library declared for itself.  Keeping
the bindings in the environment prevents a project from reaching a library it
never declared merely because something it did declare pulled that library in.

:func:`read_manifest` performs structural parsing only.  It returns the complete
open JSON object, including extension keys, without claiming that recognized
field values are valid.  :func:`load_project` is the semantic boundary: it
validates and narrows every field this loader recognizes before reading project
sources or libraries.

Every rule this module implements that another language's standard library would
decide differently is pinned explicitly rather than delegated: directory
ordering, hidden entries, symbolic links, case comparison, containment, and the
JSON dialect.

.. currentmodule:: openqasm3.project
.. autofunction:: discover
.. autofunction:: load_target(path, *, workspace_roots=(), home_dir=None)
.. autofunction:: load_project
.. autofunction:: read_manifest
.. autofunction:: collect_default_file_set
.. autofunction:: canonical_name
.. autofunction:: contained

.. autoclass:: LoadedProject
   :members:

.. autodata:: Manifest

.. autoexception:: ProjectError
   :members: identity
.. autoexception:: ManifestError
.. autoexception:: FileSetError
.. autoexception:: CanonicalNameError
.. autoexception:: ContainmentError
.. autoexception:: LibraryError

.. autodata:: MANIFEST_NAME
.. autodata:: SOURCE_SUFFIXES
.. autodata:: MAX_WALK_UP_STEPS
"""

__all__ = [
    "MANIFEST_NAME",
    "Manifest",
    "SOURCE_SUFFIXES",
    "MAX_WALK_UP_STEPS",
    "discover",
    "load_target",
    "read_manifest",
    "collect_default_file_set",
    "canonical_name",
    "contained",
    "load_project",
    "LoadedProject",
    "ProjectError",
    "ManifestError",
    "FileSetError",
    "CanonicalNameError",
    "ContainmentError",
    "LibraryError",
]

import json
import os
import unicodedata
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import (
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from .resolver import (
    LIBRARY_PREFIX,
    STANDARD_LIBRARY_NAME,
    IncludeEnvironment,
    validate_library_name,
)

PathLike = Union[str, "os.PathLike[str]"]
"""A file-system path accepted by this module.  Byte paths are not supported."""


Manifest = Dict[str, object]
"""An open, structurally parsed ``openqasm.json`` object.

Values remain raw JSON data.  In particular, this type permits extension keys and does not
claim that recognized fields have passed the semantic checks performed by
:func:`load_project`.
"""


@dataclass(frozen=True)
class _LibraryDeclaration:
    path: str


@dataclass(frozen=True)
class _ValidatedManifest:
    name: Optional[str]
    files: Optional[Tuple[str, ...]]
    programs: Optional[Tuple[str, ...]]
    libraries: Mapping[str, _LibraryDeclaration]


MANIFEST_NAME = "openqasm.json"
"""The file name that marks a directory as a project root."""

SOURCE_SUFFIXES = (".qasm", ".inc")
"""Suffixes the default file-set walk collects, compared case-sensitively."""

REPOSITORY_MARKERS = (".git", ".hg", ".svn", ".jj")
"""Directory entries that end the upward search for a manifest."""

MAX_WALK_UP_STEPS = 64
"""How many directories the upward search examines before giving up.

This is a count of directories examined, not of parent steps taken, and the
starting directory is the first examined.  A manifest one less than this many
directories above the starting directory is therefore still found, and one
directory further up is not.
"""

_PATTERN_CHARACTERS = "*?"


class ProjectError(Exception):
    """Base class for errors raised while loading a project.

    This is deliberately not a subclass of
    :class:`~openqasm3.resolver.IncludeError`.  A malformed project is not a
    failure to resolve an include target, and callers usually want to tell the
    two apart.

    Several distinct faults share a subclass, so the exception type alone does
    not say which fault occurred.  :attr:`identity` names it with a stable code
    such as ``"manifest-key-duplicate"``, which a caller can branch on.  Prefer
    it to matching the message: diagnostic text may be reworded at any time.  A
    condition with no agreed identity leaves the attribute ``None``, so test for
    the identities you handle rather than assuming one is present.
    """

    identity: Optional[str] = None
    """Stable machine-readable code naming the fault, or ``None`` when the
    condition has no agreed identity."""

    def __init__(self, *args: object, identity: Optional[str] = None) -> None:
        super().__init__(*args)
        if identity is not None:
            self.identity = identity


class ManifestError(ProjectError):
    """The manifest is missing, unreadable, or not a well-formed manifest."""


class FileSetError(ProjectError):
    """A declared file is not a usable member of the project."""


class CanonicalNameError(ProjectError):
    """Two files collide, or one claims a name it may not have."""


class ContainmentError(ProjectError):
    """A file resolves to a location outside the root that supplies it."""

    identity = "containment-escape"


class LibraryError(ProjectError):
    """A ``libraries`` declaration is malformed, unreachable, or inconsistent."""


def _reject_nonstandard_constant(literal: str):
    # Python's json accepts NaN and Infinity by default and JSON.parse rejects
    # them, so a manifest that used one would load in one language and not the
    # other.  Reject them here so both agree.
    raise ManifestError(
        "manifest contains the non-JSON constant %r" % literal,
        identity="manifest-constant-nonstandard",
    )


_MAX_EXACT_INTEGER = 2**53 - 1


def _reject_large_integer(literal: str) -> int:
    # A JSON number is a double in several languages, which holds integers exactly only to
    # this magnitude.  The check covers keys this loader does not recognize as well, because
    # a value it ignores today is one a later loader reads.
    value = int(literal)
    if abs(value) > _MAX_EXACT_INTEGER:
        raise ManifestError(
            "manifest value %s exceeds the greatest integer magnitude a manifest may depend"
            " on, %d" % (literal, _MAX_EXACT_INTEGER),
            identity="manifest-integer-too-large",
        )
    return value


def _reject_duplicate_keys(pairs):
    # Both languages silently keep the last value for a repeated key, and only
    # Python offers a hook that can see the repetition at all.
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(
                "duplicate manifest key %r" % key, identity="manifest-key-duplicate"
            )
        result[key] = value
    return result


def read_manifest(manifest_path: PathLike) -> Manifest:
    """Structurally parse the manifest at ``manifest_path``.

    :param manifest_path: Path to an ``openqasm.json`` file.
    :return: The open JSON object, including unrecognized extension keys.  Recognized field
        values remain unvalidated until the object is passed to :func:`load_project`.
    :raises ManifestError: The file cannot be read, is not well-formed JSON
        under the restrictions above, or does not hold a JSON object.
    """
    path = os.fspath(manifest_path)
    try:
        with open(path, "r", encoding="utf-8") as stream:
            text = stream.read()
    except UnicodeError as exc:
        raise ManifestError(
            "manifest '%s' must be UTF-8: %s" % (path, exc), identity="manifest-not-utf8"
        ) from exc
    except OSError as exc:
        raise ManifestError(
            "could not read manifest '%s': %s" % (path, exc), identity="manifest-unreadable"
        ) from exc
    if text.startswith("\ufeff"):
        # Python keeps a byte-order mark when reading as UTF-8 and JSON.parse
        # rejects it, so reject it in both.
        raise ManifestError(
            "manifest '%s' must be UTF-8 with no byte-order mark" % path,
            identity="manifest-byte-order-mark",
        )
    try:
        data = json.loads(
            text,
            parse_constant=_reject_nonstandard_constant,
            object_pairs_hook=_reject_duplicate_keys,
            parse_int=_reject_large_integer,
        )
    except ValueError as exc:
        raise ManifestError(
            "manifest '%s' is not valid JSON: %s" % (path, exc),
            identity="manifest-json-invalid",
        ) from exc
    if not isinstance(data, dict):
        raise ManifestError(
            "manifest '%s' must hold a JSON object" % path, identity="manifest-json-invalid"
        )
    return data


def _real(path: str) -> str:
    # Non-strict, matching os.path.realpath's default.  Node's realpathSync
    # raises for a path that does not exist, so a port must resolve the longest
    # existing ancestor and re-append the remainder rather than propagating.
    return os.path.realpath(path)


def _same_directory(first: str, second: str) -> bool:
    """Whether two paths name one directory.

    A volume that ignores case presents one directory under many spellings, and
    :func:`os.path.normcase` does not detect that outside Windows.  The file system's own
    identity does, on every platform, so it decides wherever both paths exist; the folded
    name is the fallback for a path that does not.
    """
    try:
        return os.path.samestat(os.stat(first), os.stat(second))
    except OSError:
        return os.path.normcase(_real(first)) == os.path.normcase(_real(second))


def _overlaps(first: str, second: str) -> bool:
    """Whether two roots are one directory tree, or one lies within the other.

    Decided by walking the deeper path's ancestors and comparing file system identity, so
    that two spellings of one directory cannot present as two disjoint roots.  A root of a
    load always exists, which is what lets this be identity-based where
    :func:`contained`, which must accept a path that does not, stays lexical.
    """
    return _within(first, second) or _within(second, first)


def _within(candidate: str, root: str) -> bool:
    """Whether ``candidate`` is ``root`` or lies beneath it, by file system identity."""
    try:
        root_status = os.stat(root)
    except OSError:
        return False
    current = _real(candidate)
    while True:
        try:
            if os.path.samestat(os.stat(current), root_status):
                return True
        except OSError:
            pass
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def contained(candidate: PathLike, root: PathLike) -> bool:
    """Report whether ``candidate`` is ``root`` or lies beneath it.

    Symbolic links are resolved for this test and for nothing else, so a link
    cannot be used to read outside the project while canonical names stay
    lexical.

    :param candidate: The path to test.  It need not exist.
    :param root: The project root.
    """
    real_root = _real(os.fspath(root))
    real_candidate = _real(os.fspath(candidate))
    try:
        relative = os.path.relpath(real_candidate, real_root)
    except ValueError:
        # Windows paths on different drives cannot be compared.  Node's
        # path.relative returns the other path instead of raising, so a port
        # must check for an absolute result rather than for an exception.
        return False
    # Some path implementations return an absolute path when the candidate and
    # root cannot be expressed relative to one another.
    if os.path.isabs(relative):
        return False
    # A relative path escapes the root exactly when its first component moves
    # to the parent; all other relative paths are the root or its descendants.
    return relative.split(os.sep)[0] != os.pardir


def discover(
    start_path: PathLike,
    *,
    workspace_roots: Sequence[PathLike] = (),
    home_dir: Optional[PathLike] = None,
) -> Optional[str]:
    """Find the project root for ``start_path``, searching upwards.

    :param start_path: A source file, or a directory to search from.
    :param workspace_roots: Directories the host considers open.  When supplied,
        the search does not leave them.
    :param home_dir: The user's home directory.  Defaults to the real one.
    :return: The project root, or ``None`` when the file belongs to no project
        and should be compiled on its own.

    A manifest is only detected here, never read, so a manifest that cannot be
    parsed still ends the search and is reported by :func:`load_project` rather
    than silently moving the file into a different project.

    The search stops at the first manifest, at a version-control marker, at the
    home directory, at the file-system root, or once
    :data:`MAX_WALK_UP_STEPS` directories have been examined.  When workspace
    roots are supplied, a directory outside all of them is never examined at
    all, so a manifest above the workspace cannot capture a file inside it.
    Within a directory that is examined, a manifest is tested for before a
    version-control marker, so a manifest at the root of a repository is found.
    """
    home = os.path.abspath(os.path.expanduser("~") if home_dir is None else os.fspath(home_dir))
    home = _real(home) if home is not None else None
    roots = [os.path.abspath(os.fspath(root)) for root in workspace_roots]
    start = os.path.abspath(os.fspath(start_path))
    directory = start if os.path.isdir(start) else os.path.dirname(start)

    # One directory is examined per iteration, so the bound is the iteration
    # count itself.  An implementation that loops once more disagrees with the
    # specification about a project 65 directories deep.
    for _ in range(MAX_WALK_UP_STEPS):
        if roots and not any(contained(directory, root) for root in roots):
            return None
        if os.path.isfile(os.path.join(directory, MANIFEST_NAME)):
            return directory
        if any(os.path.exists(os.path.join(directory, marker)) for marker in REPOSITORY_MARKERS):
            return None
        if home is not None and _same_directory(directory, home):
            return None
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent
    return None


def canonical_name(relative_posix: str) -> str:
    """Return the canonical name for a project-relative source name.

    The name is used exactly as given, once validated.  Nothing is normalized,
    a name is a sequence of characters the host supplied, and folding it would
    claim an equivalence the file system does not guarantee.  A consequence is
    that a non-ASCII name is only as portable as the volumes it is stored on.
    """
    _validate_relative(relative_posix, "source name")
    return relative_posix


def _ascii_fold(value: str) -> str:
    # Case-only collisions are detected with an ASCII fold rather than with full
    # case folding, because the two languages cannot agree: Python's casefold
    # maps "ss" to "ss" while JavaScript has no case-folding operation at all.
    return "".join(
        chr(ord(character) + 0x20) if "A" <= character <= "Z" else character for character in value
    )


def _claim_normalized_name(name: str, claimed: Dict[str, str], *, key_prefix: str = "") -> None:
    """Claim one name in an NFC collision domain without changing its spelling."""
    key = key_prefix + unicodedata.normalize("NFC", name)
    previous = claimed.get(key)
    if previous is not None and previous != name:
        raise CanonicalNameError(
            "canonical names differ only by Unicode normalization: %r and %r" % (previous, name),
            identity="canonical-name-normalization-collision",
        )
    claimed[key] = name


def _invalid_name(entry: str, reason: str, key: str) -> FileSetError:
    return FileSetError("%s entry %s: %r" % (key, reason, entry), identity="files-name-invalid")


def _validate_relative(entry: str, key: str) -> None:
    """Validate a project-relative POSIX source name.

    :param entry: The source name to validate.
    :param key: The manifest field or context to identify in diagnostics.
    :raises FileSetError: The name is empty, absolute, drive-qualified, contains
        a backslash or pattern character, has an empty, current-directory,
        or parent-directory component, or has a component beginning with the
        library prefix.
    """
    if not entry or entry.startswith("/") or entry.startswith("\\"):
        raise _invalid_name(entry, "must be a relative POSIX name", key)
    if "\\" in entry:
        raise _invalid_name(entry, "must not contain a backslash", key)
    if len(entry) > 1 and entry[0].isascii() and entry[0].isalpha() and entry[1] == ":":
        raise _invalid_name(entry, "must not be drive-qualified", key)
    for segment in entry.split("/"):
        if segment in ("", ".", os.pardir):
            raise _invalid_name(entry, "has an illegal component", key)
        if segment.startswith(LIBRARY_PREFIX):
            # A library canonical name is minted by a `libraries` declaration, so a
            # project-relative name that produced one would be a second, undeclared source.
            raise _invalid_name(
                entry, "must not have a component beginning with %r" % LIBRARY_PREFIX, key
            )
        if any(character in segment for character in _PATTERN_CHARACTERS):
            raise _invalid_name(entry, "must not contain a pattern", key)


def _ends_the_walk(directory: str) -> bool:
    """Whether ``directory`` begins a project or a repository of its own.

    :func:`discover` stops walking up at a manifest or a repository marker, so the walk down
    stops at the same boundaries.  Were they to disagree, a nested project's files would be
    absorbed by the project above it while discovery still assigned them to the nested one.
    """
    if os.path.isfile(os.path.join(directory, MANIFEST_NAME)):
        return True
    return any(os.path.exists(os.path.join(directory, marker)) for marker in REPOSITORY_MARKERS)


def collect_default_file_set(root: PathLike) -> Tuple[str, ...]:
    """Walk ``root`` and return its source files as project-relative names.

    This is used when the manifest has no ``files`` key.  It is a procedure
    rather than a pattern match because pattern matching is not portable: two
    widely used standard libraries differ on case sensitivity, brace expansion,
    hidden entries, result ordering, and whether ``**`` follows symbolic links.

    The walk descends no further into a directory holding a manifest or a
    repository marker, because such a directory is the extent of a project or a
    checkout of its own.  ``root`` itself is not tested, so a project's own
    manifest does not end its own walk.

    Three kinds of entry are skipped wherever they appear: one whose name begins
    with ``.``, one whose name begins with ``@`` (reserved for library canonical
    names, which only a declaration mints), and every symbolic link, so that one
    file cannot enter the file set under two names.
    """
    base = os.fspath(root)
    collected: List[str] = []

    def walk(directory: str, prefix: str) -> None:
        with os.scandir(directory) as entries:
            # Neither directory listing nor pattern matching guarantees an
            # order, so sort by encoded bytes rather than by the default
            # comparison, which is locale-sensitive in other languages.
            listing = sorted(entries, key=lambda item: item.name.encode("utf-8"))
        for item in listing:
            if item.name.startswith("."):
                continue
            if item.name.startswith(LIBRARY_PREFIX):
                # Reserved for library canonical names, which only a declaration mints.
                continue
            if item.is_symlink():
                continue
            if item.is_dir(follow_symlinks=False):
                if _ends_the_walk(item.path):
                    continue
                walk(item.path, prefix + item.name + "/")
            elif item.is_file(follow_symlinks=False) and item.name.endswith(SOURCE_SUFFIXES):
                collected.append(prefix + item.name)

    walk(base, "")
    return tuple(collected)


@dataclass(frozen=True)
class LoadedProject:
    """An immutable source and resolution snapshot loaded from one project.

    :attr:`environment` combines :attr:`sources` and :attr:`library_bindings`
    for use as :func:`openqasm3.parse`'s ``includes=`` argument.

    Fields may be appended in later versions, so read them by name.
    """

    sources: Mapping[str, str]
    """The immutable mapping from canonical name to source text."""

    programs: Optional[Tuple[str, ...]] = None
    """Project-relative source names offered for compilation, or ``None``."""

    library_bindings: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    """Immutable owner-local apparent-to-canonical library bindings.

    The outer key is the declaring project's canonical library name, and ``""``
    for this project.  Every loaded project has an entry, empty when it declares
    no libraries, so that a project given no libraries reaches none.
    """

    compilation_root: Optional[str] = None
    """The canonical name selected for compilation, or ``None`` when the caller
    named no particular source."""

    environment: IncludeEnvironment = field(init=False, repr=False, compare=False)
    """The resolution environment built from this project's immutable state."""

    def __post_init__(self) -> None:
        sources = MappingProxyType(dict(self.sources))
        library_bindings = MappingProxyType(
            {
                owner: MappingProxyType(dict(bindings))
                for owner, bindings in self.library_bindings.items()
            }
        )
        programs = None if self.programs is None else tuple(self.programs)
        object.__setattr__(self, "sources", sources)
        object.__setattr__(self, "programs", programs)
        object.__setattr__(self, "library_bindings", library_bindings)
        object.__setattr__(
            self,
            "environment",
            IncludeEnvironment.scoped(sources, library_bindings),
        )


def _manifest_at(base: str) -> Manifest:
    path = os.path.join(base, MANIFEST_NAME)
    return read_manifest(path) if os.path.isfile(path) else {}


def _validate_library_name(name: object) -> str:
    """Validate a declared library name, which becomes a canonical-name prefix."""
    try:
        return validate_library_name(name)
    except (TypeError, ValueError) as exc:
        raise LibraryError(str(exc), identity="library-declaration-invalid") from exc


def _library_path(name: str, spec: object) -> str:
    """Return the declared path for a library.

    A library is declared as an object so that ``path`` can later be joined by other
    source kinds.  An unrecognized key inside it is ignored, as elsewhere in the manifest.
    """
    if not isinstance(spec, Mapping):
        raise LibraryError(
            "library %r must be declared as an object" % name,
            identity="library-declaration-invalid",
        )
    if "$comment" in spec and not isinstance(spec["$comment"], str):
        raise LibraryError(
            "library %r '$comment' must be a string" % name,
            identity="library-declaration-invalid",
        )
    path = spec.get("path")
    if path is None:
        raise LibraryError(
            "library %r declares no source; 'path' is the only kind supported" % name,
            identity="library-declaration-invalid",
        )
    if not isinstance(path, str) or not path:
        raise LibraryError(
            "library %r has a non-string path" % name, identity="library-declaration-invalid"
        )
    if path.startswith("/") or "\\" in path:
        raise LibraryError(
            "library %r path must be a relative POSIX path: %r" % (name, path),
            identity="library-declaration-invalid",
        )
    if len(path) > 1 and path[0].isascii() and path[0].isalpha() and path[1] == ":":
        raise LibraryError(
            "library %r path must not be drive-qualified: %r" % (name, path),
            identity="library-declaration-invalid",
        )
    return path


def _string_array(
    manifest: Mapping[str, object], key: str, identity: str
) -> Optional[Tuple[str, ...]]:
    if key not in manifest:
        return None
    declared = manifest[key]
    if not isinstance(declared, list):
        raise ManifestError("'%s' must be an array of strings" % key, identity=identity)
    entries: List[str] = []
    for entry in declared:
        if not isinstance(entry, str):
            raise ManifestError("'%s' must be an array of strings" % key, identity=identity)
        entries.append(entry)
    return tuple(entries)


def _validated_libraries(
    manifest: Mapping[str, object],
) -> Mapping[str, _LibraryDeclaration]:
    if "libraries" not in manifest:
        return {}
    declared = manifest["libraries"]
    if not isinstance(declared, Mapping):
        raise LibraryError("'libraries' must be an object", identity="library-declaration-invalid")

    apparent_names: Dict[str, str] = {}
    declarations: List[Tuple[str, object]] = []
    for apparent, spec in declared.items():
        name = _validate_library_name(apparent)
        _claim_normalized_name(name, apparent_names)
        declarations.append((name, spec))

    libraries: Dict[str, _LibraryDeclaration] = {}
    for apparent, spec in sorted(declarations, key=lambda item: item[0]):
        libraries[apparent] = _LibraryDeclaration(path=_library_path(apparent, spec))
    return libraries


def _validate_manifest(manifest: Mapping[str, object]) -> _ValidatedManifest:
    """Validate and narrow every manifest field this loader recognizes."""
    if "$comment" in manifest and not isinstance(manifest["$comment"], str):
        raise ManifestError("'$comment' must be a string")
    name = _validate_library_name(manifest["name"]) if "name" in manifest else None
    files = _string_array(manifest, "files", "files-declaration-invalid")
    if files is not None:
        for entry in files:
            _validate_relative(entry, "files")
    libraries = _validated_libraries(manifest)
    programs = _string_array(manifest, "programs", "programs-declaration-invalid")
    if programs is not None:
        for entry in programs:
            _validate_relative(entry, "programs")

    return _ValidatedManifest(
        name=name,
        files=files,
        programs=programs,
        libraries=libraries,
    )


def _declared_library_name(apparent: str, root: str) -> Tuple[str, _ValidatedManifest]:
    """The canonical name a library declares for itself, with its manifest.

    A library's identity cannot come from the project that uses it, because the name that
    project writes is local to it: two projects may use one name for different libraries, and
    one library may be reached under different names.  So a library declares its own name, and
    a directory that declares none is not a library.
    """
    manifest_path = os.path.join(root, MANIFEST_NAME)
    if not os.path.isfile(manifest_path):
        raise LibraryError(
            "library %r has no %s, so it declares no name to be known by"
            % (apparent, MANIFEST_NAME),
            identity="library-name-undeclared",
        )
    raw_manifest = read_manifest(manifest_path)
    if "name" not in raw_manifest:
        raise LibraryError(
            "library %r declares no 'name' in its %s" % (apparent, MANIFEST_NAME),
            identity="library-name-undeclared",
        )
    manifest = _validate_manifest(raw_manifest)
    canonical = manifest.name
    if canonical is None:
        raise LibraryError(
            "library %r declares no 'name' in its %s" % (apparent, MANIFEST_NAME),
            identity="library-name-undeclared",
        )
    return canonical, manifest


def _load_libraries(
    base: str,
    manifest: _ValidatedManifest,
    owner: str,
    sources: Dict[str, str],
    folded: Dict[str, str],
    bound: Dict[str, str],
    canonical_names: Dict[str, str],
    library_bindings: Dict[str, Dict[str, str]],
    stack: Tuple[str, ...],
) -> None:
    """Load every library ``manifest`` declares, and their libraries in turn.

    ``owner`` is the declaring project's own canonical library name, ``""`` for the project
    being loaded.  ``bound`` maps a canonical library name to the root it was minted from, so
    that one library reached twice is loaded once and two libraries claiming one name collide.
    Its values, with the compilation root, are also every root bound so far, which is what a
    new root must not overlap.
    """
    apparent_map = library_bindings.setdefault(owner, {})
    declared = manifest.libraries
    if not declared:
        return

    for apparent in sorted(declared):
        path = declared[apparent].path
        library_root = _real(os.path.join(base, *path.split("/")))

        if not os.path.isdir(library_root):
            raise LibraryError(
                "library %r does not exist: %r" % (apparent, path), identity="library-missing"
            )
        if any(_same_directory(active, library_root) for active in stack):
            raise LibraryError(
                "library %r closes a cycle back to a project already being loaded: %r"
                % (apparent, library_root),
                identity="library-cycle",
            )
        # Every root already taking part in this load, the compilation root first.
        for other in (stack[0],) + tuple(bound.values()):
            if _same_directory(other, library_root):
                continue
            if _overlaps(other, library_root):
                raise LibraryError(
                    "library %r declares a root that overlaps another root of this load:"
                    " %r and %r. The roots of one load are disjoint trees, so that no file"
                    " is reachable under two canonical names" % (apparent, other, library_root),
                    identity="library-root-overlap",
                )

        canonical, library_manifest = _declared_library_name(apparent, library_root)
        _claim_normalized_name(canonical, canonical_names)
        apparent_map[apparent] = canonical

        previous = bound.get(canonical)
        if previous is not None:
            if _same_directory(previous, library_root):
                # The same library reached again under any name; already loaded.
                continue
            raise LibraryError(
                "library name %r is declared by two different roots: %r and %r"
                % (canonical, previous, library_root),
                identity="library-binding-conflict",
            )

        bound[canonical] = library_root
        _load_files(
            library_root, library_manifest, LIBRARY_PREFIX + canonical + "/", sources, folded
        )
        _load_libraries(
            library_root,
            library_manifest,
            canonical,
            sources,
            folded,
            bound,
            canonical_names,
            library_bindings,
            stack + (library_root,),
        )


def _load_files(
    base: str,
    manifest: _ValidatedManifest,
    prefix: str,
    sources: Dict[str, str],
    folded: Dict[str, str],
    compilation_root: Optional[str] = None,
) -> Dict[str, str]:
    """Load one project's own files, prefixing each canonical name, and return them.

    ``compilation_root`` is the one canonical name permitted to be the reserved
    standard-library name, because a compilation root is handed to an implementation directly
    rather than reached through include resolution.
    """
    if manifest.files is None:
        entries: Iterable[str] = collect_default_file_set(base)
    else:
        entries = manifest.files

    own: Dict[str, str] = {}
    # Every name-level fault is decided over the whole declared list before any file is
    # opened, so that a diagnostic does not depend on whether the volume distinguishes case.
    resolved: List[Tuple[str, str]] = []
    seen: Dict[str, str] = {}
    for entry in entries:
        _validate_relative(entry, "files")
        name = prefix + canonical_name(entry)
        if name == STANDARD_LIBRARY_NAME and name != compilation_root:
            raise CanonicalNameError(
                "a project file may not take the reserved canonical name %r, because an"
                " implementation resolves that target before consulting the project and so"
                " could never reach the file. The rule does not apply to a file selected as"
                " the compilation root, which is not reached through include resolution"
                % STANDARD_LIBRARY_NAME,
                identity="canonical-name-reserved",
            )
        if name in sources or name in seen:
            raise CanonicalNameError(
                "duplicate canonical name: %r" % name, identity="canonical-name-duplicate"
            )
        # The two folds stay separate: composing them would make the Kelvin sign, whose
        # canonical decomposition is "K", collide with "k".
        case_key = "case:" + _ascii_fold(name)
        previous = folded.get(case_key)
        if previous is not None:
            raise CanonicalNameError(
                "canonical names differ only by case: %r and %r" % (previous, name),
                identity="canonical-name-case-collision",
            )
        # DictResolver unifies its keys under NFC and raises when two collide, but that layer
        # cannot name the files.  Detect it here, where both paths can be reported.
        _claim_normalized_name(name, folded, key_prefix="nfc:")
        folded[case_key] = name
        seen[name] = entry
        resolved.append((entry, name))

    for entry, name in resolved:
        absolute = os.path.join(base, *entry.split("/"))
        if not contained(absolute, base):
            raise ContainmentError("file escapes the root that supplies it: %r" % entry)
        if os.path.islink(absolute):
            raise FileSetError(
                "file %r is a symbolic link. A source unit is never reached through one,"
                " so that a single file cannot take two canonical names" % entry,
                identity="files-symbolic-link",
            )
        try:
            with open(absolute, "r", encoding="utf-8") as stream:
                text = stream.read()
        except FileNotFoundError as exc:
            raise FileSetError("file does not exist: %r" % entry, identity="files-missing") from exc
        except UnicodeError as exc:
            raise FileSetError(
                "file is not UTF-8: %r: %s" % (entry, exc), identity="files-not-utf8"
            ) from exc
        except OSError as exc:
            raise FileSetError(
                "could not read %r: %s" % (entry, exc), identity="files-unreadable"
            ) from exc
        sources[name] = text
        own[name] = text
    return own


def load_project(
    root: PathLike,
    *,
    manifest: Optional[Mapping[str, object]] = None,
    compilation_root: Optional[str] = None,
) -> "LoadedProject":
    """Load a project and its declared libraries into one immutable snapshot.

    Use :func:`openqasm3.parse_project` to parse a source through the snapshot's
    :attr:`LoadedProject.environment`.  :attr:`LoadedProject.programs` preserves
    the corresponding manifest field and names only this project's own files.

    A library declared in ``libraries`` is loaded as a project in its own right,
    from a root outside the one referencing it.  The name a project writes for a
    library is local to that project; the library's own manifest declares the
    ``name`` its files take canonical names under, as ``@name/``.  Two projects
    may therefore use one name for different libraries, and one library may be
    reached under different names without being loaded twice.

    :param root: The project root.
    :param manifest: A manifest already in hand.  When omitted, the manifest is
        read from ``root`` if one is present there, and an empty manifest is
        assumed otherwise.
    :param compilation_root: The canonical name of the file selected for
        compilation, when one is known.  Only that name may take the reserved
        standard-library canonical name: an implementation resolves
        ``stdgates.inc`` before consulting the project, so a file-set member
        holding that name could never be reached, but a compilation root is
        handed to the implementation directly.  :func:`load_target` supplies
        this; a caller loading a project without selecting a target has no
        compilation root to name.
    :raises ManifestError: The manifest is unreadable, malformed, or requires a
        capability this loader does not provide.
    :raises FileSetError: A declared file is invalid or missing, or a declared
        program is not a member of the file set.
    :raises CanonicalNameError: Two project-defined names collide, or a file
        claims the reserved standard-library name.
    :raises ContainmentError: A file lies outside the root that supplies it.
    :raises LibraryError: A ``libraries`` declaration is malformed, names a root
        that is missing, not external, or declares no name of its own, binds
        inconsistently, or closes a cycle.
    """
    base = _real(os.fspath(root))
    raw_manifest: Mapping[str, object]
    if manifest is None:
        raw_manifest = _manifest_at(base)
    else:
        raw_manifest = manifest
    validated_manifest = _validate_manifest(raw_manifest)

    sources: Dict[str, str] = {}
    folded: Dict[str, str] = {}
    bound: Dict[str, str] = {}
    canonical_names: Dict[str, str] = {}
    library_bindings: Dict[str, Dict[str, str]] = {}
    own = _load_files(base, validated_manifest, "", sources, folded, compilation_root)
    _load_libraries(
        base,
        validated_manifest,
        "",
        sources,
        folded,
        bound,
        canonical_names,
        library_bindings,
        (base,),
    )

    return LoadedProject(
        sources=sources,
        programs=_declared_programs(validated_manifest, own),
        library_bindings=library_bindings,
        compilation_root=compilation_root,
    )


def load_target(
    path: PathLike,
    *,
    workspace_roots: Sequence[PathLike] = (),
    home_dir: Optional[PathLike] = None,
) -> "LoadedProject":
    """Load the project containing a selected source file, or that file alone.

    :param path: The existing regular source file selected for compilation.
    :param workspace_roots: Directories the host considers open.  These have
        the same discovery semantics as in :func:`discover`.
    :param home_dir: The discovery boundary used by :func:`discover`.
    :return: The loaded project, whose :attr:`~LoadedProject.compilation_root`
        is the selected file's canonical name.
    :raises FileSetError: The target is not an existing regular file, or a
        discovered project's file set excludes it.

    When discovery finds no manifest, the selected file is loaded in a
    synthetic one-file project rooted at its containing directory.  Existing
    :func:`discover` and :func:`load_project` callers can continue to use those
    lower-level operations directly.
    """
    target = os.path.abspath(os.fspath(path))
    if not os.path.isfile(target):
        raise FileSetError(
            "target is not an existing regular file: %r" % os.fspath(path),
            identity="target-not-a-file",
        )

    root = discover(target, workspace_roots=workspace_roots, home_dir=home_dir)
    if root is None:
        name = canonical_name(os.path.basename(target))
        return load_project(
            os.path.dirname(target), manifest={"files": [name]}, compilation_root=name
        )

    relative = os.path.relpath(target, root).replace(os.sep, "/")
    name = canonical_name(relative)
    loaded = load_project(root, compilation_root=name)
    if name not in loaded.sources:
        hint = "; it is a symbolic link, which the default file set excludes" * os.path.islink(
            target
        )
        raise FileSetError(
            "selected target is not a member of the project file set: %r%s" % (name, hint),
            identity="target-not-in-file-set",
        )
    return loaded


def _declared_programs(
    manifest: _ValidatedManifest, sources: Mapping[str, str]
) -> Optional[Tuple[str, ...]]:
    declared = manifest.programs
    if declared is None:
        return None

    programs: List[str] = []
    seen = set()
    for entry in declared:
        # Membership is byte-exact, as it is for a file-set entry.
        name = canonical_name(entry)
        if name not in sources:
            raise FileSetError(
                "programs entry is not a member of the file set: %r" % entry,
                identity="programs-name-unknown",
            )
        if name in seen:
            raise FileSetError(
                "duplicate programs entry: %r" % entry,
                identity="programs-name-duplicate",
            )
        seen.add(name)
        programs.append(name)
    return tuple(programs)
