"""
===========================================
Include resolution (``openqasm3.resolver``)
===========================================

Support for resolving ``include`` statements when parsing OpenQASM 3 programs.

An *include target* is the string literal written in an ``include`` statement.
It is an opaque logical name; the specification does not require it to be a
file-system path.  An :class:`IncludeEnvironment` forms *candidate canonical
names* from an include target and the canonical name of the source unit
containing the ``include`` statement.  An :class:`IncludeResolver` maps one
canonical name to source text and the canonical source identity that text was
resolved to.  A source identity is a nonempty opaque string owned by its
resolver.  The parser compares identities exactly but does not require them to
be paths, URIs, or portable logical names.

The parser leaves includes unresolved when ``includes`` is ``None``.  It also
accepts a complete :class:`IncludeEnvironment`, or one of three raw source
backends that it wraps with :meth:`IncludeEnvironment.unscoped`: a mapping from
canonical name to source text, a callable taking ``(canonical_name)``, or an
:class:`IncludeResolver` instance.  :func:`as_resolver` normalizes those three
backend forms.

.. currentmodule:: openqasm3.resolver
.. autoclass:: IncludeEnvironment
    :members:
.. autoclass:: IncludeResolver
.. autoclass:: ResolvedSource
.. autoclass:: DictResolver
.. autoclass:: FunctionResolver
.. autoclass:: ChoiceResolver
.. autoclass:: StandardLibraryResolver
.. autodata:: IncludeSource
.. autofunction:: as_resolver
.. autofunction:: library_root
.. autofunction:: library_name
.. autofunction:: validate_source_identity
.. autofunction:: validate_library_name
.. autofunction:: validate_include_target
.. autofunction:: flatten_includes

.. autodata:: MINIMUM_INCLUDE_DEPTH
.. autodata:: DEFAULT_MAX_INCLUDE_DEPTH
.. autodata:: ROOT_RELATIVE_PREFIX
.. autodata:: LIBRARY_PREFIX
.. autodata:: STANDARD_LIBRARY_NAME

.. autoexception:: IncludeError
   :members: identity
.. autoexception:: IncludeNotFoundError
.. autoexception:: CyclicIncludeError
.. autoexception:: IncludeDepthExceededError
.. autoexception:: InvalidIncludeTargetError
.. autoexception:: AmbiguousIncludeTargetError
.. autoexception:: InconsistentResolutionError
"""

__all__ = [
    "IncludeEnvironment",
    "IncludeResolver",
    "ResolvedSource",
    "DictResolver",
    "FunctionResolver",
    "ChoiceResolver",
    "StandardLibraryResolver",
    "as_resolver",
    "library_root",
    "library_name",
    "validate_source_identity",
    "validate_library_name",
    "validate_include_target",
    "IncludeSource",
    "flatten_includes",
    "IncludeError",
    "IncludeNotFoundError",
    "CyclicIncludeError",
    "IncludeDepthExceededError",
    "InvalidIncludeTargetError",
    "AmbiguousIncludeTargetError",
    "InconsistentResolutionError",
    "MINIMUM_INCLUDE_DEPTH",
    "DEFAULT_MAX_INCLUDE_DEPTH",
    "ROOT_RELATIVE_PREFIX",
    "LIBRARY_PREFIX",
    "STANDARD_LIBRARY_NAME",
]

import abc
import re
import unicodedata
from collections.abc import Mapping as _AbcMapping
from types import MappingProxyType
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

from . import ast

MINIMUM_INCLUDE_DEPTH = 15
"""The inclusion depth this parser guarantees to support.

The specification leaves any depth limit implementation defined, so this is this parser's own
guarantee rather than a conformance requirement.
"""

DEFAULT_MAX_INCLUDE_DEPTH = 64
"""The inclusion depth this parser supports, which is at least :data:`MINIMUM_INCLUDE_DEPTH`."""


class IncludeError(Exception):
    """Base class for errors raised while resolving an ``include`` statement.

    This is deliberately not a subclass of :class:`~openqasm3.parser.QASM3ParsingError`, so that
    resolution can be used without the ``[parser]`` extra installed.

    :attr:`identity` names the fault with a stable machine-readable code, so that a caller, or a
    test suite written against another implementation, can branch on the fault rather than on
    diagnostic text, which may be reworded at any time.  A condition with no agreed identity
    leaves the attribute ``None``, so test for the identities you handle rather than assuming one
    is present.

    Every error in this package carries :attr:`identity` the same way: a subclass that always
    names one fault fixes it as a class attribute, and a subclass covering several supplies the
    one that applies when it is raised.
    """

    identity: Optional[str] = None
    """Stable machine-readable code naming the fault, or ``None`` when the condition has no
    agreed identity."""

    def __init__(self, *args, identity: Optional[str] = None):
        super().__init__(*args)
        if identity is not None:
            self.identity = identity


class IncludeNotFoundError(IncludeError):
    """No resolver could supply source text for an include target."""

    identity = "include-not-found"


class CyclicIncludeError(IncludeError):
    """An include target resolved to a source unit that is currently being incorporated."""

    identity = "include-cycle"


class IncludeDepthExceededError(IncludeError):
    """Inclusion nested more deeply than this parser supports."""

    identity = "include-depth-exceeded"


class InvalidIncludeTargetError(IncludeError):
    """An include target is not well formed, such as one containing a ``.`` or ``..`` component."""

    identity = "include-target-invalid"


class AmbiguousIncludeTargetError(IncludeError):
    """An include target matched more than one candidate canonical name."""

    identity = "include-target-ambiguous"


class InconsistentResolutionError(IncludeError):
    """A resolver answered the same question two different ways within one parse.

    This reports a fault in the host rather than in the source: resolution must be a function of
    the target and its includer for a program's meaning to be well defined.

    Carries ``"include-resolution-inconsistent-target"`` when one target resolved to two
    different source units, and ``"include-resolution-inconsistent-source"`` when one canonical
    name supplied two different texts.
    """


_FunctionResult = Union[None, str, "ResolvedSource", Tuple[str, str]]

_ResolverSource = Union[
    Mapping[str, str],
    Callable[[str], _FunctionResult],
    "IncludeResolver",
]
IncludeSource = Union[None, _ResolverSource, "IncludeEnvironment"]
"""Anything :func:`openqasm3.parse` accepts as ``includes``."""


class ResolvedSource(NamedTuple):
    """The result of successfully resolving an include target.

    Read the fields by name.  Later versions may append fields, so unpacking or
    indexing a result will not keep working.
    """

    source: str
    """The OpenQASM source text of the resolved source unit."""

    canonical_name: str
    """The opaque source identity the target resolved to."""


class IncludeResolver(abc.ABC):
    """Maps a canonical name to the source unit it names.

    Subclasses implement :meth:`lookup`.  Returning ``None`` means "this resolver does not supply
    that source unit", which allows resolvers to be composed with :class:`ChoiceResolver`.  A
    resolver that owns a name but cannot load it should raise :class:`IncludeError` instead, so
    that a genuine failure is not mistaken for a miss.
    """

    @abc.abstractmethod
    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        """Return the source unit for ``canonical_name``, or ``None`` if this resolver has none.

        A resolver may return a different canonical name than the one asked for, which is how a
        resolver unifies spellings that name one source unit.  It does not choose which names are
        asked for; that is the environment's candidate rule.  The returned identity must be a
        nonempty string, but its spelling and interpretation belong to this resolver.

        This is called once per candidate name, so more than once for a single ``include``
        statement, and again for the same name while resolution is checked for consistency.  It
        must therefore be free of side effects, and must return the same result for the same name
        throughout one parse; the parser raises :class:`InconsistentResolutionError` if it does
        not.  A resolver that counts calls or meters a network fetch has to cache accordingly.
        """
        raise NotImplementedError


ROOT_RELATIVE_PREFIX = "//"
"""Marks an include target as naming a source unit from the root of the includer's library."""

LIBRARY_PREFIX = "@"
"""Marks a canonical name as belonging to a named library rather than to the program itself."""

STANDARD_LIBRARY_NAME = "stdgates.inc"
"""The reserved canonical name of the standard library, which is never scoped to a library.

The reservation exists so that a source unit inside a library can reach the standard library at
all.
"""


def validate_source_identity(identity: object) -> str:
    """Return a nonempty source ``identity`` without interpreting or normalizing it.

    A resolver owns the identity of the source it returns.  The parser compares identities for
    exact string equality but does not require a path, URI, or other naming scheme.
    """
    if not isinstance(identity, str):
        raise TypeError(f"a source identity must be a string, not {type(identity).__name__}")
    if not identity:
        raise ValueError("a source identity must not be empty")
    return identity


def validate_library_name(name: object) -> str:
    """Return ``name`` if it is a portable bare library name.

    Library names are logical name components used on both sides of environment bindings.  The ``@``
    selector and path separators belong to include-target syntax rather than to the name.
    """
    if not isinstance(name, str):
        raise TypeError(f"a library name must be a string, not {type(name).__name__}")
    if not name:
        raise ValueError("a library name must not be empty")
    if name.startswith(LIBRARY_PREFIX) or "/" in name or "\\" in name:
        raise ValueError(
            f"library name {name!r} must not begin with '@' or contain a path separator"
        )
    if name in (".", "..") or "*" in name or "?" in name:
        raise ValueError(f"library name {name!r} is not a portable name component")
    return name


def library_root(canonical_name: Optional[str]) -> str:
    """The prefix bounding ``canonical_name``'s library, or ``""`` when it is not in one.

    The boundary is carried by the name itself, so deriving it needs no other state.  Translating
    an apparent library name into a canonical one does need other state; see
    :meth:`IncludeEnvironment.candidates`.
    """
    if canonical_name and canonical_name.startswith(LIBRARY_PREFIX):
        separator = canonical_name.find("/")
        if separator >= 0:
            return canonical_name[: separator + 1]
    return ""


def library_name(canonical_name: Optional[str]) -> str:
    """The canonical library name ``canonical_name`` belongs to, or ``""`` when it is in none.

    This is :func:`library_root` without the surrounding ``@`` and ``/``, which are selector
    syntax rather than part of a library's name.  It is the key a library map is looked up under.
    """
    return library_root(canonical_name)[len(LIBRARY_PREFIX) : -1]


_DRIVE_QUALIFIED = re.compile(r"^[A-Za-z]:")


def _invalid_target(target: str, includer: Optional[str], reason: str) -> InvalidIncludeTargetError:
    location = f" in '{includer}'" if includer else ""
    return InvalidIncludeTargetError(f"include target '{target}'{location} {reason}")


def validate_include_target(target: str, *, includer: Optional[str] = None) -> None:
    """Raise :class:`InvalidIncludeTargetError` if ``target`` is not a well-formed include target.

    An include target is an opaque logical name rather than a file-system path, but a program is
    portable only when the same target names the same source unit on every host.  The forms
    rejected here are exactly those the environments implementations run in interpret differently,
    so accepting them would make a program's meaning depend on the machine compiling it.

    OpenQASM string literals have no escape sequences, so a backslash written in an include target
    reaches this function as a literal backslash and is rejected rather than read as a separator.
    """
    if not target:
        raise _invalid_target(target, includer, "is empty")
    if "\\" in target:
        raise _invalid_target(
            target,
            includer,
            "contains a '\\' character; components of an include target are separated by '/'",
        )
    body = target
    if target.startswith(ROOT_RELATIVE_PREFIX):
        body = target[len(ROOT_RELATIVE_PREFIX) :]
        if not body:
            raise _invalid_target(target, includer, "names no source unit after '//'")
        if body.startswith(LIBRARY_PREFIX):
            raise _invalid_target(
                target,
                includer,
                "combines '//' with a library; a library target already names its own root",
            )
    elif target.startswith("/"):
        raise _invalid_target(
            target,
            includer,
            "is absolute; an include target is resolved with respect to its includer,"
            " or with respect to the root of the includer's library when written as '//name'",
        )
    elif target.startswith(LIBRARY_PREFIX):
        library, _, remainder = target[len(LIBRARY_PREFIX) :].partition("/")
        if not library or not remainder:
            raise _invalid_target(
                target,
                includer,
                "names a library but no source unit within it; write '@library/name'",
            )
    _validate_components(body, lambda reason: _invalid_target(target, includer, reason))


def _validate_components(body: str, fault: Callable[[str], IncludeError]) -> None:
    """Apply the checks a canonical name and an include target share to ``body``."""
    if _DRIVE_QUALIFIED.match(body):
        raise fault("begins with a drive specifier, which is not portable")
    for component in body.split("/"):
        if component in (".", ".."):
            raise fault(f"contains a '{component}' path component, which is not permitted")
        if not component:
            raise fault("contains an empty path component")


class DictResolver(IncludeResolver):
    """Resolves canonical names against an in-memory mapping of canonical name to source text.

    This is the appropriate resolver for notebooks, test harnesses, language servers holding
    unsaved buffers, and any other host that already has its sources in memory.

    A name that does not match a key exactly is matched again under Unicode Normalization Form
    C, so that a host whose file system stores names decomposed reaches the same source unit as
    one whose file system does not.  The mapping's own key is returned as the canonical name.

    :raises AmbiguousIncludeTargetError: Two keys differ only by normalization, so the requested
        name matches both.
    """

    def __init__(self, mapping: _AbcMapping):
        self._mapping = {validate_source_identity(name): source for name, source in mapping.items()}
        self._normalized: Dict[str, List[str]] = {}
        for name in self._mapping:
            self._normalized.setdefault(unicodedata.normalize("NFC", name), []).append(name)

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        if canonical_name in self._mapping:
            return ResolvedSource(self._mapping[canonical_name], canonical_name)
        names = self._normalized.get(unicodedata.normalize("NFC", canonical_name))
        if names is None:
            return None
        if len(names) > 1:
            matches = ", ".join(f"'{name}'" for name in names)
            raise AmbiguousIncludeTargetError(
                f"canonical name '{canonical_name}' matches more than one mapping key under"
                f" Unicode Normalization Form C ({matches})"
            )
        name = names[0]
        return ResolvedSource(self._mapping[name], name)

    def __repr__(self):
        return f"{type(self).__name__}({{...{len(self._mapping)} sources...}})"


class FunctionResolver(IncludeResolver):
    """Resolves canonical names by calling a user-supplied function.

    The function is called as ``function(canonical_name)``.  It may return ``None``, the source
    text, a :class:`ResolvedSource`, or a ``(source, canonical_name)`` pair when it unifies
    several spellings onto one source unit.
    """

    def __init__(self, function: "Callable[[str], _FunctionResult]"):
        self._function = function

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        result = self._function(canonical_name)
        if result is None:
            return None
        if isinstance(result, str):
            return ResolvedSource(result, canonical_name)
        # Indexed rather than unpacked so that a longer ResolvedSource still works.
        return ResolvedSource(result[0], result[1])

    def __repr__(self):
        return f"{type(self).__name__}({self._function!r})"


class ChoiceResolver(IncludeResolver):
    """Consults each of ``resolvers`` in order and returns the first source unit found.

    Only ``None`` moves on to the next resolver.  An exception from a member propagates and ends
    the chain, so a resolver that owns a name but cannot load it stops the search rather than
    letting a later resolver answer for it.
    """

    def __init__(self, resolvers: Iterable[IncludeResolver]):
        self._resolvers = list(resolvers)

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        for resolver in self._resolvers:
            resolved = resolver.lookup(canonical_name)
            if resolved is not None:
                return resolved
        return None

    def __repr__(self):
        return f"{type(self).__name__}({self._resolvers!r})"


class StandardLibraryResolver(IncludeResolver):
    """Resolves the specification-defined standard library without source text.

    The reference parser records the reserved ``"stdgates.inc"`` source identity but does not
    define its gates. Downstream compiler tooling resolves the standard-library symbols and their
    language-version-specific implementations.
    """

    _TARGET = STANDARD_LIBRARY_NAME

    def lookup(self, canonical_name: str) -> Optional[ResolvedSource]:
        if canonical_name == self._TARGET:
            return ResolvedSource("", self._TARGET)
        return None


def as_resolver(includes: Optional[_ResolverSource]) -> Optional[IncludeResolver]:
    """Normalize a raw source backend onto an :class:`IncludeResolver`.

    Mappings, callables, and resolver objects are the three backend forms.  ``None`` is returned
    unchanged and means that includes are not resolved.
    """
    if includes is None or isinstance(includes, IncludeResolver):
        return includes
    if isinstance(includes, _AbcMapping):
        return DictResolver(includes)
    if callable(includes):
        return FunctionResolver(includes)
    raise TypeError(
        "'includes' must be None, a mapping of canonical name to source, a callable taking"
        f" (canonical_name), or an IncludeResolver, but got {type(includes).__name__}"
    )


def _freeze_bindings(
    bindings: Mapping[str, Mapping[str, str]],
) -> Mapping[str, Mapping[str, str]]:
    if not isinstance(bindings, _AbcMapping):
        raise TypeError("'bindings' must be a mapping of library names to mappings")
    copied = {}
    for owner, library_bindings in bindings.items():
        validated_owner = "" if owner == "" else validate_library_name(owner)
        if not isinstance(library_bindings, _AbcMapping):
            raise TypeError(f"the library bindings for {owner!r} must be a mapping")
        copied[validated_owner] = MappingProxyType(
            {
                validate_library_name(apparent): validate_library_name(canonical)
                for apparent, canonical in library_bindings.items()
            }
        )
    return MappingProxyType(copied)


def _unambiguous_form(canonical_name: str, includer: str) -> str:
    root = library_root(includer)
    if root and canonical_name.startswith(root):
        return ROOT_RELATIVE_PREFIX + canonical_name[len(root) :]
    if canonical_name.startswith(LIBRARY_PREFIX):
        return canonical_name
    return ROOT_RELATIVE_PREFIX + canonical_name


class IncludeEnvironment:
    """A source resolver and the library-name bindings that govern its lookups.

    Construct an environment with :meth:`unscoped` when apparent library names are already
    canonical, or with :meth:`scoped` when every source owner has an explicit set of available
    libraries.
    """

    def __init__(
        self,
        resolver: IncludeResolver,
        bindings: Optional[Mapping[str, Mapping[str, str]]],
    ):
        self._resolver = ChoiceResolver([StandardLibraryResolver(), resolver])
        self._bindings = None if bindings is None else _freeze_bindings(bindings)

    @classmethod
    def unscoped(cls, includes: _ResolverSource) -> "IncludeEnvironment":
        """Construct an environment where apparent library names are canonical as written."""
        resolver = as_resolver(includes)
        if resolver is None:
            raise TypeError("'includes' must supply source lookup when constructing an environment")
        return cls(resolver, None)

    @classmethod
    def scoped(
        cls,
        includes: _ResolverSource,
        bindings: Mapping[str, Mapping[str, str]],
    ) -> "IncludeEnvironment":
        """Construct an environment with an immutable snapshot of owner-local bindings."""
        resolver = as_resolver(includes)
        if resolver is None:
            raise TypeError("'includes' must supply source lookup when constructing an environment")
        return cls(resolver, bindings)

    def candidates(self, target: str, includer: str) -> Tuple[str, ...]:
        """Return the candidate canonical names for ``target`` inside ``includer``.

        Every candidate is consulted without precedence.  A scoped environment returns no
        candidate when the includer's bindings do not declare an apparent library name.
        """
        validate_source_identity(includer)
        validate_include_target(target, includer=includer)
        if target == STANDARD_LIBRARY_NAME:
            return (target,)
        root = library_root(includer)
        if target.startswith(ROOT_RELATIVE_PREFIX):
            return (root + target[len(ROOT_RELATIVE_PREFIX) :],)
        if target.startswith(LIBRARY_PREFIX):
            if self._bindings is None:
                return (target,)
            apparent, _, remainder = target[len(LIBRARY_PREFIX) :].partition("/")
            owner_bindings = self._bindings.get(library_name(includer))
            if owner_bindings is None:
                return ()
            canonical = owner_bindings.get(apparent)
            if canonical is None:
                return ()
            return (LIBRARY_PREFIX + canonical + "/" + remainder,)
        candidates = []
        separator = includer.rfind("/")
        if separator >= 0:
            candidates.append(includer[: separator + 1] + target)
        scoped = root + target
        if scoped not in candidates:
            candidates.append(scoped)
        return tuple(candidates)

    def resolve(self, target: str, includer: str) -> ResolvedSource:
        """Resolve ``target`` from ``includer`` to exactly one source unit."""
        candidates = self.candidates(target, includer)
        matches: List[Tuple[str, ResolvedSource]] = []
        for candidate in candidates:
            resolved = self._resolver.lookup(candidate)
            if resolved is not None:
                validate_source_identity(resolved.canonical_name)
                matches.append((candidate, resolved))
        if not matches:
            message = f"could not resolve include target '{target}' from '{includer}'"
            if not candidates:
                apparent = target[len(LIBRARY_PREFIX) :].partition("/")[0]
                message += (
                    f"; no library named '{apparent}' is available to '{includer}'."
                    " A source unit reaches only the libraries its own library bindings name"
                )
            elif target.startswith(LIBRARY_PREFIX):
                message += (
                    f"; '{candidates[0]}' was tried and no resolver supplied it."
                    " A library target is translated to a canonical name before any resolver"
                    " is consulted, so the resolver must be able to supply that name"
                )
            elif "/" not in includer and not target.startswith(ROOT_RELATIVE_PREFIX):
                message += (
                    f"; '{includer}' has no name prefix, so only '{target}' itself was tried."
                    " Pass name= to give the source a canonical name that include targets can be"
                    " resolved with respect to"
                )
            raise IncludeNotFoundError(message)
        distinct: List[Tuple[str, ResolvedSource]] = []
        for candidate, resolved in matches:
            previous = next(
                (seen for seen in distinct if resolved.canonical_name == seen[1].canonical_name),
                None,
            )
            if previous is None:
                distinct.append((candidate, resolved))
            elif previous[1].source != resolved.source:
                raise InconsistentResolutionError(
                    f"canonical name '{resolved.canonical_name}' produced different source text",
                    identity="include-resolution-inconsistent-source",
                )
        if len(distinct) > 1:
            names = ", ".join(f"'{resolved.canonical_name}'" for _, resolved in distinct)
            remedies = " or ".join(
                f"'{_unambiguous_form(candidate, includer)}'" for candidate, _ in distinct
            )
            raise AmbiguousIncludeTargetError(
                f"include target '{target}' in '{includer}' matches more than one source unit"
                f" ({names}); write {remedies} to say which is meant"
            )
        return distinct[0][1]


def flatten_includes(program: ast.Program) -> ast.Program:
    """Return a copy of ``program`` with resolved includes spliced into the statement list.

    Each source unit is spliced at most once, matching the specification's rule that a source unit
    is incorporated into a program at most once per canonical name.  An ``include`` statement that
    was not resolved is left in place.

    An ``include`` whose ``source`` index names no source unit is left in place too, rather than
    dropped: that can only happen in a hand-built program, where discarding a statement would
    lose information the caller has and this function does not.

    The nodes of the returned program are shared with ``program``; only the statement lists are new.
    """
    by_index = {index: unit for index, unit in enumerate(program.sources)}
    incorporated: Set[str] = {program.sources[0].canonical_name} if program.sources else set()

    def splice(
        statements: Sequence[Union[ast.Statement, ast.Pragma]],
    ) -> List[Union[ast.Statement, ast.Pragma]]:
        result: List[Union[ast.Statement, ast.Pragma]] = []
        for statement in statements:
            if not isinstance(statement, ast.Include) or statement.source is None:
                result.append(statement)
                continue
            unit = by_index.get(statement.source)
            if unit is None:
                result.append(statement)
                continue
            if unit.canonical_name in incorporated:
                continue
            incorporated.add(unit.canonical_name)
            result.extend(splice(unit.statements or []))
        return result

    flattened = ast.Program(statements=splice(program.statements), version=program.version)
    flattened.span = program.span
    flattened.sources = list(program.sources)
    return flattened
