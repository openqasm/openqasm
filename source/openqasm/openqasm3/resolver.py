"""
===========================================
Include resolution (``openqasm3.resolver``)
===========================================

Support for resolving ``include`` statements when parsing OpenQASM 3 programs.

An *include target* is the string literal written in an ``include`` statement.
It is an opaque logical name; the specification does not require it to be a
file-system path.  A *resolver* maps an include target, together with the
canonical name of the source unit containing the ``include`` statement, to
source text and the canonical name that text was resolved to.

Four load behaviours are supported wherever a resolver is accepted:

1. ``None``: includes are not resolved and no source is loaded.
2. A mapping from canonical name to source text.
3. A callable taking ``(target, includer)``.
4. An :class:`IncludeResolver` instance.

:func:`as_resolver` normalises the first three onto the fourth.

.. currentmodule:: openqasm3.resolver
.. autoclass:: IncludeResolver
.. autoclass:: ResolvedSource
.. autoclass:: DictResolver
.. autoclass:: FunctionResolver
.. autoclass:: ChoiceResolver
.. autoclass:: StandardLibraryResolver
.. autofunction:: as_resolver
.. autofunction:: candidate_names
.. autofunction:: validate_include_target
.. autofunction:: flatten_includes

.. autoexception:: IncludeError
.. autoexception:: IncludeNotFoundError
.. autoexception:: CyclicIncludeError
.. autoexception:: IncludeDepthExceededError
.. autoexception:: InvalidIncludeTargetError
"""

__all__ = [
    "IncludeResolver",
    "ResolvedSource",
    "DictResolver",
    "FunctionResolver",
    "ChoiceResolver",
    "StandardLibraryResolver",
    "as_resolver",
    "candidate_names",
    "flatten_includes",
    "IncludeError",
    "IncludeNotFoundError",
    "CyclicIncludeError",
    "IncludeDepthExceededError",
    "InvalidIncludeTargetError",
    "MINIMUM_INCLUDE_DEPTH",
    "DEFAULT_MAX_INCLUDE_DEPTH",
]

import abc
import re
import unicodedata
from collections.abc import Mapping as _AbcMapping
from typing import Callable, Iterable, List, NamedTuple, Optional, Sequence, Tuple, Union

from . import ast

MINIMUM_INCLUDE_DEPTH = 15
"""The inclusion depth the OpenQASM 3 specification requires implementations to support."""

DEFAULT_MAX_INCLUDE_DEPTH = 64
"""The inclusion depth this parser supports, which must be at least :data:`MINIMUM_INCLUDE_DEPTH`."""


class IncludeError(Exception):
    """Base class for errors raised while resolving an ``include`` statement.

    This is deliberately not a subclass of :class:`~openqasm3.parser.QASM3ParsingError`, so that
    resolution can be used without the ``[parser]`` extra installed.
    """


class IncludeNotFoundError(IncludeError):
    """No resolver could supply source text for an include target."""


class CyclicIncludeError(IncludeError):
    """An include target resolved to a source unit that is currently being incorporated."""


class IncludeDepthExceededError(IncludeError):
    """Inclusion nested more deeply than this parser supports."""


class InvalidIncludeTargetError(IncludeError):
    """An include target is not well formed, such as one containing a ``.`` or ``..`` component."""


class ResolvedSource(NamedTuple):
    """The result of successfully resolving an include target."""

    source: str
    """The OpenQASM source text of the resolved source unit."""

    canonical_name: str
    """The canonical name the target resolved to.  This is the source unit's identity."""


class IncludeResolver(abc.ABC):
    """Maps an include target plus its includer's canonical name to source text.

    Subclasses implement :meth:`resolve`.  Returning ``None`` means "this resolver does not handle
    that target", which allows resolvers to be composed with :class:`ChoiceResolver`.  A resolver
    that owns a target but cannot load it should raise :class:`IncludeError` instead, so that a
    genuine failure is not mistaken for a miss.
    """

    @abc.abstractmethod
    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        """Resolve ``target``, as written in a source unit whose canonical name is ``includer``."""
        raise NotImplementedError


def candidate_names(target: str, includer: Optional[str]) -> List[str]:
    """Candidate canonical names for ``target`` written inside ``includer``, in priority order.

    The name prefix of the including source unit is tried first, so that an include target is
    resolved with respect to its includer rather than any ambient state, then the target is tried
    on its own.  An includer with no prefix, such as the default name given to a program parsed
    from a string, contributes no extra candidate.
    """
    candidates = []
    if includer:
        separator = max(includer.rfind("/"), includer.rfind("\\"))
        if separator >= 0:
            candidates.append(includer[: separator + 1] + target)
    candidates.append(target)
    return candidates


_DRIVE_QUALIFIED = re.compile(r"^[A-Za-z]:")


def _invalid_target(target: str, includer: Optional[str], reason: str) -> InvalidIncludeTargetError:
    location = f" in '{includer}'" if includer else ""
    return InvalidIncludeTargetError(f"include target '{target}'{location} {reason}")


def validate_include_target(target: str, includer: Optional[str] = None) -> None:
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
    if target.startswith("/"):
        raise _invalid_target(
            target,
            includer,
            "is absolute; an include target is resolved with respect to its includer",
        )
    if _DRIVE_QUALIFIED.match(target):
        raise _invalid_target(
            target, includer, "begins with a drive specifier, which is not portable"
        )
    for component in target.split("/"):
        if component in (".", ".."):
            raise _invalid_target(
                target, includer, f"contains a '{component}' path component, which is not permitted"
            )
        if not component:
            raise _invalid_target(target, includer, "contains an empty path component")


class DictResolver(IncludeResolver):
    """Resolves include targets against an in-memory mapping of canonical name to source text.

    This is the appropriate resolver for notebooks, test harnesses, language servers holding
    unsaved buffers, and any other host that already has its sources in memory.

    A target that does not match a key exactly is matched again under Unicode Normalization Form
    C, so that a host whose file system stores names decomposed reaches the same source unit as
    one whose file system does not.  The mapping's own key is returned as the canonical name.
    """

    def __init__(self, mapping: _AbcMapping):
        self._mapping = dict(mapping)
        self._normalised: dict = {}
        for name in self._mapping:
            self._normalised.setdefault(unicodedata.normalize("NFC", name), name)

    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        for candidate in candidate_names(target, includer):
            if candidate in self._mapping:
                return ResolvedSource(self._mapping[candidate], candidate)
            name = self._normalised.get(unicodedata.normalize("NFC", candidate))
            if name is not None:
                return ResolvedSource(self._mapping[name], name)
        return None

    def __repr__(self):
        return f"{type(self).__name__}({{...{len(self._mapping)} sources...}})"


class FunctionResolver(IncludeResolver):
    """Resolves include targets by calling a user-supplied function.

    The function is called as ``function(target, includer)``.  It may return ``None`` to indicate
    that it does not handle the target, a ``(source, canonical_name)`` pair, or a bare string,
    in which case the include target itself is used as the canonical name.
    """

    def __init__(self, function: Callable[[str, str], Union[None, str, Tuple[str, str]]]):
        self._function = function

    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        result = self._function(target, includer)
        if result is None:
            return None
        if isinstance(result, str):
            return ResolvedSource(result, target)
        source, canonical_name = result
        return ResolvedSource(source, canonical_name)

    def __repr__(self):
        return f"{type(self).__name__}({self._function!r})"


class ChoiceResolver(IncludeResolver):
    """Consults each of ``resolvers`` in order and returns the first successful result."""

    def __init__(self, resolvers: Iterable[IncludeResolver]):
        self._resolvers = list(resolvers)

    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        for resolver in self._resolvers:
            resolved = resolver.resolve(target, includer)
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

    _TARGET = "stdgates.inc"

    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        if target == self._TARGET:
            return ResolvedSource("", self._TARGET)
        return None


def as_resolver(includes) -> Optional[IncludeResolver]:
    """Normalise any of the four supported load behaviours onto an :class:`IncludeResolver`.

    ``None`` is returned unchanged, and means that includes are not resolved.
    """
    if includes is None or isinstance(includes, IncludeResolver):
        return includes
    if isinstance(includes, _AbcMapping):
        return DictResolver(includes)
    if callable(includes):
        return FunctionResolver(includes)
    raise TypeError(
        "'includes' must be None, a mapping of canonical name to source, a callable taking"
        f" (target, includer), or an IncludeResolver, but got {type(includes).__name__}"
    )


def flatten_includes(program: ast.Program) -> ast.Program:
    """Return a copy of ``program`` with resolved includes spliced into the statement list.

    Each source unit is spliced at most once, matching the specification's rule that a source unit
    is incorporated into a program at most once per canonical name.  An ``include`` statement that
    was not resolved is left in place.

    The nodes of the returned program are shared with ``program``; only the statement lists are new.
    """
    by_index = {index: unit for index, unit in enumerate(program.sources)}
    incorporated: set = set()

    def splice(statements: Sequence) -> List:
        result: List = []
        for statement in statements:
            if not isinstance(statement, ast.Include) or statement.source is None:
                result.append(statement)
                continue
            unit = by_index.get(statement.source)
            if unit is None or unit.canonical_name in incorporated:
                continue
            incorporated.add(unit.canonical_name)
            result.extend(splice(unit.statements or []))
        return result

    flattened = ast.Program(statements=splice(program.statements), version=program.version)
    flattened.span = program.span
    flattened.sources = list(program.sources)
    return flattened
