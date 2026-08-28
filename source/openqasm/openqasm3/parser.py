"""
=============================
Parser (``openqasm3.parser``)
=============================

Tools for parsing OpenQASM 3 programs into the :obj:`reference AST <openqasm3.ast>`.

The quick-start interface is simply to call ``openqasm3.parse``:

.. currentmodule:: openqasm3
.. autofunction:: openqasm3.parse
.. autofunction:: parse_project
.. autofunction:: derive_programs

The rest of this module provides some lower-level internals of the parser.

.. currentmodule:: openqasm3.parser
.. autofunction:: span
.. autofunction:: add_span
.. autofunction:: combine_span
.. autofunction:: get_span
.. autofunction:: get_comments
.. autoclass:: QASMNodeVisitor
.. autoexception:: QASM3ParsingError
.. autoexception:: MissingVersionWarning

.. autodata:: DEFAULT_SOURCE_NAME
.. autodata:: DEFAULT_VERSION
.. autodata:: FEATURE_MIN_VERSION
"""

# pylint: disable=wrong-import-order

__all__ = [
    "parse",
    "parse_project",
    "derive_programs",
    "get_span",
    "add_span",
    "combine_span",
    "span",
    "QASMNodeVisitor",
    "QASM3ParsingError",
    "MissingVersionWarning",
    "get_comments",
    "DEFAULT_SOURCE_NAME",
]

import re
import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Mapping, Union, TypeVar, List, Optional, Protocol, Tuple, cast

try:
    from antlr4 import (
        CommonTokenStream,
        InputStream,
        ParserRuleContext,
        RecognitionException,
    )
    from antlr4.error.Errors import ParseCancellationException
    from antlr4.error.ErrorStrategy import BailErrorStrategy
    from antlr4.tree.Tree import TerminalNode
    from antlr4.error.ErrorListener import ErrorListener
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from ._antlr.qasm3Lexer import qasm3Lexer  # type: ignore[import-not-found]
from ._antlr.qasm3Parser import qasm3Parser  # type: ignore[import-not-found]
from ._antlr.qasm3ParserVisitor import qasm3ParserVisitor  # type: ignore[import-not-found]
from . import ast, spec
from .resolver import (
    LIBRARY_PREFIX,
    STANDARD_LIBRARY_NAME,
    CyclicIncludeError,
    DEFAULT_MAX_INCLUDE_DEPTH,
    IncludeDepthExceededError,
    IncludeEnvironment,
    ResolvedSource,
    validate_source_identity,
    validate_include_target,
    IncludeSource,
    InconsistentResolutionError,
)

_TYPE_NODE_INIT = {
    "int": ast.IntType,
    "uint": ast.UintType,
    "float": ast.FloatType,
    "angle": ast.AngleType,
}


class MissingVersionWarning(UserWarning):
    """Warned when the root source unit has no ``OPENQASM`` version header and
    OpenQASM 3.0 is assumed in its place.

    The version statement is optional, so this is not an error.  It has its own
    category so that callers who deliberately parse headerless fragments can
    silence just this diagnostic::

        warnings.filterwarnings("ignore", category=MissingVersionWarning)
    """


class QASM3ParsingError(Exception):
    """An error raised while parsing a program into the reference AST.

    ``identity`` optionally names a fault with a stable code that a caller can branch on.
    Prefer it to matching the diagnostic message, which may be reworded.  A fault with no
    agreed identity leaves the attribute ``None``.
    """

    identity: Optional[str] = None
    """Stable machine-readable code naming the fault, or ``None`` when the condition has no
    agreed identity."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        *,
        identity: Optional[str] = None,
    ) -> None:
        if line is not None and column is not None:
            prefix = f"L{line}:C{column}: "
        elif line is not None:
            prefix = f"L{line}: "
        else:
            prefix = ""

        super().__init__(f"{prefix}{message}")
        self.line = line
        self.column = column
        if identity is not None:
            self.identity = identity


class _RaiseOnErrorListener(ErrorListener):
    """Raises exception for all errors handled by this listener."""

    def syntaxError(
        self,
        recognizer: object,
        offendingSymbol: object,
        line: int,
        column: int,
        msg: str,
        exc: RecognitionException,
    ):
        raise QASM3ParsingError(msg, line=line, column=column) from exc


class _OperatorToken(Protocol):
    text: str


class _BinaryExpressionContext(Protocol):
    """Describes the attributes for binary-expression types.

    This enables static type checking to correctly infer attribute types.
    """

    op: _OperatorToken

    def expression(self, index: Optional[int] = None) -> ParserRuleContext: ...


class _TokenWithSpan(Protocol):
    line: int
    column: int
    start: int
    stop: int


class _TerminalNodeWithSymbol(Protocol):
    """Captures the token attribute the generated terminal nodes expose for spans."""

    symbol: _TokenWithSpan


_VERSION_NUM = re.compile(r"\d+(\.\d+)*")
_VERSION_KEYWORD = re.compile(
    r"\A(?:(?:\s+)|(?://[^\n]*(?:\n|\Z))|(?:/\*.*?\*/))*OPENQASM\b",
    re.DOTALL,
)
_VERSION_HEADER = re.compile(
    r"\A(?:(?:\s+)|(?://[^\n]*(?:\n|\Z))|(?:/\*.*?\*/))*" r"OPENQASM\s+(?P<version>\d+(?:\.\d+)*)",
    re.DOTALL,
)


def parse_version(prog: str) -> Optional[Tuple[int, ...]]:
    """Extract the version number from a potential OpenQASM program.

    If there is a syntactically valid ``OPENQASM <version>`` statement (with or without the
    necessary semicolon) as the first non-comment statement of the file, the ``<version>`` is
    returned as a tuple of ``int``.  If not, ``None`` is returned.

    This function can return version numbers even for programs that are not syntactically valid; it
    is used as an initial test to set the version of the parser appropriately.

    This function may return version tuples that are longer than two parts, although OpenQASM 2.0
    and 3.0 both specified a maximum of two components.
    """
    in_multiline_comment = False
    found_openqasm = False
    for line in prog.splitlines():
        while line:
            line = line.strip()
            if in_multiline_comment:
                if (loc := line.find("*/")) < 0:
                    break
                line = line[loc + 2 :]
                in_multiline_comment = False
                continue
            if line.startswith("//"):
                break
            if line.startswith("/*"):
                in_multiline_comment = True
                line = line[2:]
                continue
            if found_openqasm:
                # If here, we've got a non-space, non-comment token after an `OPENQASM` one, so it's
                # either a valid version or the file is syntactically invalid.
                if (m := _VERSION_NUM.match(line)) is not None:
                    return tuple(int(x) for x in m.group(0).split("."))
                return None
            if line.startswith("OPENQASM"):
                found_openqasm = True
                line = line[len("OPENQASM") :]
                continue
            # We've got a non-OPENQASM token as the first non-comment token, so there's no
            # syntactically valid version statement.
            return None
    return None


def _parse_spec_version(version: str) -> Tuple[int, ...]:
    """Convert a version string such as ``3.1`` to a tuple."""
    return tuple(int(part) for part in version.split("."))


def _normalize_version(version: Tuple[int, ...]) -> Tuple[int, ...]:
    """Return a version tuple with an explicit minor component.

    A major-only declaration such as ``OPENQASM 3;`` parses as ``(3,)``.
    Appending ``0`` makes it ``(3, 0)``, so tuple comparisons treat it the
    same as ``OPENQASM 3.0;``. Versions that already have a minor component
    are returned unchanged.
    """
    if len(version) == 1:
        return version + (0,)
    return version


def _format_version(version: Tuple[int, ...]) -> str:
    """Return integer version components in dotted OpenQASM notation."""
    return ".".join(str(part) for part in version)


def _normalized_version_string(version: Tuple[int, ...]) -> str:
    """Return a version tuple as normalized public AST metadata."""
    return _format_version(_normalize_version(version))


def _mask_ignored_version_suffix(input_: str, version: Tuple[int, ...]) -> str:
    """Hide unsupported extra components from ANTLR without shifting source positions.

    The lexer's ``VersionSpecifier`` is ``[0-9]+ ('.' [0-9]+)?``, so it stops after the minor
    component and the remaining ``.1`` of a header like ``OPENQASM 3.0.1;`` becomes a syntax
    error.  Rewriting the header to ``3.0`` is what lets ``ignore_version`` reach the body.
    """
    # Only three or more components can trip the lexer; anything shorter is already valid.
    if len(version) <= 2:
        return input_
    # `parse_version` scans leniently and accepts headers this regex does not, such as one
    # preceded by an unterminated block comment.  Passing those through unchanged keeps ANTLR's
    # diagnostic pointing at the real defect instead of at text this function invented.
    match = _VERSION_HEADER.match(input_)
    if match is None:
        return input_
    # Span of the digits alone, so the `OPENQASM` keyword, any leading comments and everything
    # after the header are copied through verbatim.
    start, end = match.span("version")
    accepted = ".".join(match.group("version").split(".")[:2])
    # Dropping components always shortens the text, so pad the difference back with spaces: the
    # lexer skips whitespace before the `;`, and holding the total width constant keeps every
    # later token at the offset, line and column it has in `input_`, which is what the spans on
    # the returned AST refer to.
    return input_[:start] + accepted.ljust(end - start) + input_[end:]


DEFAULT_VERSION = (3, 0)
"""The language-defined effective version of a root source unit without a version header."""

_SUPPORTED_VERSIONS = frozenset(
    _normalize_version(_parse_spec_version(version)) for version in spec.supported_versions
)

FEATURE_MIN_VERSION: Dict[str, Tuple[int, ...]] = {
    "switch": (3, 1),
    "anonymous_scope": (3, 1),
    "nop": (3, 2),
}
"""The specification version that introduced each version-gated language feature.

A feature appearing in a source unit whose effective version is earlier than its
entry here is rejected where it appears.  Features absent from this mapping are
available at every supported version.
"""


def _validate_supported_version(version: Tuple[int, ...]) -> None:
    """Reject headers this parser cannot interpret under the published specification."""
    version_str = _format_version(version)
    if len(version) > 2:
        raise QASM3ParsingError(
            f"version must be '<major>' or '<major>.<minor>', not '{version_str}'",
            identity="version-malformed",
        )
    normalized = _normalize_version(version)
    if normalized in _SUPPORTED_VERSIONS:
        return
    major = normalized[0]
    if major == 2:
        raise QASM3ParsingError(
            f"OpenQASM 2 is not supported by this parser; found version '{version_str}'",
            identity="version-openqasm2",
        )
    supported_majors = sorted({supported[0] for supported in _SUPPORTED_VERSIONS})
    if major not in supported_majors:
        supported = ", ".join(f"{supported}.x" for supported in supported_majors)
        raise QASM3ParsingError(
            f"major version {major} is not supported; this parser supports OpenQASM "
            f"{supported} (found '{version_str}')",
            identity="version-major-unsupported",
        )
    minimum = min(_SUPPORTED_VERSIONS)
    maximum = max(_SUPPORTED_VERSIONS)
    if normalized < minimum:
        raise QASM3ParsingError(
            f"version '{version_str}' precedes the minimum supported version "
            f"'{_format_version(minimum)}'",
            identity="version-below-minimum",
        )
    if normalized > maximum:
        raise QASM3ParsingError(
            f"version '{version_str}' exceeds the maximum supported version "
            f"'{_format_version(maximum)}'",
            identity="version-above-maximum",
        )
    supported = ", ".join(_format_version(supported) for supported in sorted(_SUPPORTED_VERSIONS))
    raise QASM3ParsingError(
        f"version '{version_str}' is not supported; this parser supports {supported}",
        identity="version-unsupported",
    )


DEFAULT_SOURCE_NAME = "<input>"
"""Canonical name given to a source unit parsed from a string when the caller supplies no
name.  Include targets in that source unit are resolved with respect to this name."""


def _parse_to_program(
    input_: str,
    permissive: bool,
    effective_version: Optional[Tuple[int, ...]] = None,
    declared_version: Optional[Tuple[int, ...]] = None,
    ignore_version: bool = False,
) -> ast.Program:
    """Build a program using one version for feature gates and one for header metadata."""
    # The grammar's VersionSpecifier only matches `<major>[.<minor>]`, so a longer header such as
    # `OPENQASM 3.0.1;` is a syntax error before any version check runs; masking the extra
    # components is what lets `ignore_version` parse it at all.  The declaration is put back on
    # `program.version` below, so the masking is invisible in the returned AST.
    parser_input = (
        _mask_ignored_version_suffix(input_, declared_version)
        if ignore_version and declared_version is not None
        else input_
    )
    lexer = qasm3Lexer(InputStream(parser_input))
    stream = CommonTokenStream(lexer)
    parser = qasm3Parser(stream)
    if not permissive:
        # For some reason, the Python 3 runtime for ANTLR 4 is missing the
        # setter method `setErrorHandler`, so we have to set the attribute
        # directly.
        parser._errHandler = BailErrorStrategy()
        # Raise on lexer errors
        lexer.addErrorListener(_RaiseOnErrorListener())
    try:
        tree = parser.program()
    except RecognitionException as exc:
        raise QASM3ParsingError(exc.message) from exc
    except ParseCancellationException as exc:
        raise QASM3ParsingError("parse failed") from exc
    program = QASMNodeVisitor(
        version=effective_version, ignore_version=ignore_version
    ).visitProgram(tree)
    if ignore_version and declared_version is not None:
        program.version = _format_version(declared_version)
    return program


def _rebase_spans(node, source_index: int) -> None:
    """Reassign span provenance for an AST subgraph.

    Starting from ``node``, this walks every reachable :class:`ast.QASMNode` and rewrites
    ``current.span.source`` to ``source_index`` when a span is present.  Traversal follows:

    - attributes of AST nodes via ``__dict__.values()``
    - nested ``list`` and ``tuple`` containers

    A visited-ID set avoids revisiting the same object, so shared references and accidental
    cycles are handled safely.
    """
    stack = [node]
    seen = set()
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, ast.QASMNode):
            if current.span is not None:
                current.span.source = source_index
            stack.extend(current.__dict__.values())
        elif isinstance(current, (list, tuple)):
            stack.extend(current)


@dataclass
class _IncludeResolutionContext:
    """Per-parse state and helpers for resolving ``include`` statements.

    The context owns the environment, source-unit table, canonical-name indices, and consistency
    checks that must be shared across recursive include resolution.
    """

    environment: IncludeEnvironment
    permissive: bool
    sources: List[ast.SourceUnit]
    indices: Dict[str, int]
    resolved_targets: Dict[Tuple[str, str], ResolvedSource]
    canonical_sources: Dict[str, str]
    root_version: Tuple[int, ...]
    ignore_version: bool
    max_depth: int = DEFAULT_MAX_INCLUDE_DEPTH

    @classmethod
    def for_root(
        cls,
        environment: IncludeEnvironment,
        permissive: bool,
        root_name: str,
        root_ast_version: Optional[str],
        root_version: Tuple[int, ...],
        ignore_version: bool,
    ) -> "_IncludeResolutionContext":
        return cls(
            environment=environment,
            permissive=permissive,
            sources=[
                ast.SourceUnit(
                    canonical_name=root_name,
                    version=root_ast_version,
                    effective_version=_normalized_version_string(root_version),
                )
            ],
            indices={root_name: 0},
            resolved_targets={},
            canonical_sources={},
            root_version=root_version,
            ignore_version=ignore_version,
        )

    def resolve_statements(self, statements, includer: str, stack: List[str]) -> None:
        """Resolve every ``include`` statement reachable from ``statements``, in place."""
        for statement in statements:
            if isinstance(statement, ast.Include):
                self.resolve_include(statement, includer, stack)

    def resolve_include(self, statement: ast.Include, includer: str, stack: List[str]) -> None:
        """Resolve one ``include`` statement and incorporate its source unit if needed.

        This validates the target, checks resolution consistency, annotates the include statement
        with its resolved canonical name and source index, and enforces cycle, depth and
        incorporate-once rules before parsing any newly reached source text.
        """
        target = statement.target
        validate_include_target(target, includer=includer)
        resolved = self.environment.resolve(target, includer)
        self._check_consistency(target, includer, resolved)
        statement.canonical_name = resolved.canonical_name
        if resolved.canonical_name in stack:
            chain = " -> ".join(stack + [resolved.canonical_name])
            raise CyclicIncludeError(f"inclusion cycle detected: {chain}")
        existing = self.indices.get(resolved.canonical_name)
        if existing is not None:
            # The source unit is already incorporated, so this statement contributes nothing.
            statement.source = existing
            return
        if len(stack) >= self.max_depth:
            raise IncludeDepthExceededError(
                f"inclusion of '{resolved.canonical_name}' from '{includer}' exceeds the"
                f" supported inclusion depth of {self.max_depth}"
            )
        self._incorporate_source(statement, resolved, stack)

    def _check_consistency(self, target: str, includer: str, resolved: ResolvedSource) -> None:
        previous = self.resolved_targets.get((target, includer))
        if previous is None:
            self.resolved_targets[(target, includer)] = resolved
        elif previous != resolved:
            raise InconsistentResolutionError(
                f"inconsistent include resolution for target '{target}' from '{includer}'",
                identity="include-resolution-inconsistent-target",
            )
        previous_source = self.canonical_sources.get(resolved.canonical_name)
        if previous_source is None:
            self.canonical_sources[resolved.canonical_name] = resolved.source
        elif previous_source != resolved.source:
            raise InconsistentResolutionError(
                f"inconsistent include resolution for canonical name '{resolved.canonical_name}'",
                identity="include-resolution-inconsistent-source",
            )

    def _incorporate_source(
        self, statement: ast.Include, resolved: ResolvedSource, stack: List[str]
    ) -> None:
        index = len(self.sources)
        unit = ast.SourceUnit(
            canonical_name=resolved.canonical_name,
            effective_version=_normalized_version_string(self.root_version),
        )
        self.sources.append(unit)
        self.indices[resolved.canonical_name] = index
        statement.source = index

        if not resolved.source:
            # Virtual sources such as stdgates.inc have no parser-owned text; ANTLR cannot visit
            # an empty program, so represent their resolved source unit directly.
            unit.statements = []
            return

        declared_version = parse_version(resolved.source)
        if declared_version is not None and not self.ignore_version:
            _validate_supported_version(declared_version)
            normalized_declared = _normalize_version(declared_version)
            normalized_root = _normalize_version(self.root_version)
            if normalized_declared > normalized_root:
                root_str = _format_version(self.root_version)
                declared_str = _format_version(declared_version)
                raise QASM3ParsingError(
                    f"included file '{resolved.canonical_name}' declares version "
                    f"'{declared_str}' which exceeds root version '{root_str}'",
                    identity="include-version-exceeds-root",
                )
        effective_version = self.root_version
        unit.effective_version = _normalized_version_string(effective_version)
        included = _parse_to_program(
            resolved.source,
            self.permissive,
            effective_version=effective_version,
            declared_version=declared_version,
            ignore_version=self.ignore_version,
        )
        included.effective_version = unit.effective_version
        _rebase_spans(included, index)
        unit.statements = included.statements
        version = included.version
        unit.version = version
        self.resolve_statements(
            included.statements, resolved.canonical_name, stack + [resolved.canonical_name]
        )


def _validate_include_targets(statements, includer: Optional[str]) -> None:
    for statement in statements:
        if isinstance(statement, ast.Include):
            validate_include_target(statement.target, includer=includer)


def parse(
    input_: str,
    *,
    permissive: bool = False,
    ignore_version: bool = False,
    includes: IncludeSource = None,
    name: Optional[str] = None,
) -> ast.Program:
    """
    Parse a complete OpenQASM 3 program from a string.

    :param input_: A string containing a complete OpenQASM 3 program.
    :param permissive: A Boolean controlling whether ANTLR should attempt to
        recover from incorrect input or not.  Defaults to ``False``; if set to
        ``True``, the reference AST produced may be invalid if ANTLR emits any
        warning messages during its parsing phase.
    :param ignore_version: If true, ignore the specified version of the OpenQASM program, and
        attempt to parse it anyway.  There is no guarantee that the output was syntactically or
        semantically valid for the given version if this is set.  Declared, defaulted, and
        inherited effective-version metadata is still retained, while support validation,
        included-declaration ceiling validation, missing-header warnings, and version feature
        gates are bypassed.
    :param includes: How to resolve ``include`` statements.  Pass ``None`` (the default) to leave
        includes unresolved, a complete :class:`~openqasm3.resolver.IncludeEnvironment`, or a raw
        source backend: a mapping of canonical name to source text, a callable taking
        ``(canonical_name)``, or an :class:`~openqasm3.resolver.IncludeResolver`.  Raw source
        backends create an unscoped environment.  No file-system access is performed unless the
        caller supplies a backend that performs it, such as
        :class:`~openqasm3.filesystem.FileSystemResolver`.
    :param name: The source identity of ``input_``.  This is the identity that relative include
        targets are resolved with respect to.  Defaults to ``"<input>"``, which has no name
        prefix.  A source identity is any nonempty string; its spelling and interpretation belong
        to the host or resolver that owns it.
    :return: A complete :obj:`~ast.Program` node.  Its ``version`` retains the declared root
        header, while ``effective_version`` records the normalized version used for parsing.
        A root without a header has the language-defined effective version ``3.0``.
    """
    root_name = DEFAULT_SOURCE_NAME if name is None else validate_source_identity(name)
    declared_version = parse_version(input_)
    version: Tuple[int, ...]
    if declared_version is None:
        version = DEFAULT_VERSION
        if not ignore_version and _VERSION_KEYWORD.match(input_) is None:
            version_str = _format_version(version)
            warnings.warn(
                f"no version header found; defaulting to OpenQASM {version_str}. "
                f"Consider adding 'OPENQASM {version_str};' as the first non-comment line.",
                MissingVersionWarning,
                stacklevel=2,
            )
    else:
        version = declared_version
    if not ignore_version:
        _validate_supported_version(version)
    program = _parse_to_program(
        input_,
        permissive,
        effective_version=version,
        declared_version=declared_version,
        ignore_version=ignore_version,
    )
    program.effective_version = _normalized_version_string(version)
    _validate_include_targets(program.statements, root_name)
    program.sources = [
        ast.SourceUnit(
            canonical_name=root_name,
            version=program.version,
            effective_version=program.effective_version,
        )
    ]
    if includes is None:
        return program
    environment = (
        includes
        if isinstance(includes, IncludeEnvironment)
        else IncludeEnvironment.unscoped(includes)
    )
    context = _IncludeResolutionContext.for_root(
        environment, permissive, root_name, program.version, version, ignore_version
    )
    context.resolve_statements(program.statements, root_name, [root_name])
    program.sources = context.sources
    return program


class _Project(Protocol):
    @property
    def sources(self) -> Mapping[str, str]: ...

    @property
    def environment(self) -> IncludeEnvironment: ...

    @property
    def compilation_root(self) -> Optional[str]: ...


def parse_project(
    project: _Project,
    name: Optional[str] = None,
    *,
    permissive: bool = False,
    ignore_version: bool = False,
) -> ast.Program:
    """Parse one source unit from a loaded project and resolve its includes.

    :param project: A project snapshot that supplies sources, an include environment, and an
        optional compilation root.
    :param name: The source to parse.  When omitted, the project's compilation root is used.
    :param permissive: Forwarded to :func:`parse`.
    :param ignore_version: Forwarded to :func:`parse`.
    :return: The parsed program with its includes incorporated.
    :raises ValueError: No source was selected, or the selected source is absent from the project.
    :raises TypeError: An explicit source name is not a string.
    """
    if name is None:
        selected = project.compilation_root
        if selected is None:
            raise ValueError("'name' is required when the project has no compilation root")
    else:
        selected = validate_source_identity(name)
    if selected not in project.sources:
        raise ValueError(f"source {selected!r} is not present in the project")
    return parse(
        project.sources[selected],
        permissive=permissive,
        ignore_version=ignore_version,
        includes=project.environment,
        name=selected,
    )


def _include_targets(source: str, *, includer: Optional[str] = None) -> Tuple[str, ...]:
    """Return the validated, unresolved include targets one source unit writes, in order."""
    program = _parse_to_program(source, permissive=False)
    _validate_include_targets(program.statements, includer)
    return tuple(
        statement.target for statement in program.statements if isinstance(statement, ast.Include)
    )


def derive_programs(
    project: _Project,
) -> Tuple[str, ...]:
    """The source units of a project that no other source unit in it includes.

    This answers the question a project manifest's ``programs`` key answers when it is
    declared: which source units are meant to be compiled.  It is deliberately separate from
    :func:`openqasm3.project.load_project`, which reports only what a manifest declared and
    needs no parser, so that a project holding one unparseable file still loads.

    :param project: A project snapshot that supplies source text and its include environment.
        A source name beginning with
        ``@`` belongs to a library rather than to the project, so it is neither a candidate
        program nor a source of inclusions: a source unit that only something outside the
        project includes is not a program, because compiling it alone loses everything its
        includer had established.
    :return: The derived programs, in file-set order.  When every source unit is included by
        another, which is what a cycle of inclusions produces, every source unit is returned;
        that is a rule rather than a permission, so two hosts derive the same set.
    :raises QASM3ParsingError: A source unit could not be parsed.

    Include targets are formed through the project's environment rather than matched as text,
    because one candidate carries the including unit's name prefix; matching text derives the
    wrong edges whenever two source units share a base name, and no edge at all for a ``//`` or
    library target.  A target with more than one candidate present contributes an edge to each,
    which can only widen the set of units considered included.  The reserved standard-library
    name resolves outside the project and is not an inclusion for this purpose.

    The derivation is a heuristic.  A library in which no source unit includes another derives
    every source unit as a program, which is the opposite of what its author meant; declaring
    ``"programs": []`` is how the author says so.
    """
    sources = project.sources
    own = [name for name in sources if not name.startswith(LIBRARY_PREFIX)]
    included = set()
    for includer in own:
        for target in _include_targets(sources[includer], includer=includer):
            if target == STANDARD_LIBRARY_NAME:
                continue
            for candidate in project.environment.candidates(target, includer):
                if candidate in sources:
                    included.add(candidate)
    derived = tuple(name for name in own if name not in included)
    return derived or tuple(own)


def get_span(node: Union[ParserRuleContext, TerminalNode]) -> ast.Span:
    """Get the span of a node"""
    if isinstance(node, ParserRuleContext):
        # A rule that matched no tokens, such as a program holding only comments, has no stop
        # token; its span is empty at the start position.
        stop = node.start if node.stop is None else node.stop
        return ast.Span(node.start.line, node.start.column, stop.line, stop.column)
    else:
        # Terminal nodes carry their position via the generated `symbol` token.
        token_with_position = cast(_TerminalNodeWithSymbol, node).symbol
        return ast.Span(
            token_with_position.line,
            token_with_position.column,
            token_with_position.line,
            token_with_position.column + (token_with_position.stop - token_with_position.start),
        )


def get_comments(input_: str) -> List[dict]:
    """Extract comments from OpenQASM 3 source code.

    :param input_: A string containing OpenQASM 3 source code.
    :return: A list of dictionaries, one per comment, each with the keys
        ``'type'`` (either ``'line'`` or ``'block'``), ``'text'`` (the comment
        text, including its markers), ``'line'`` and ``'column'`` (where the
        comment starts).
    """
    input_stream = InputStream(input_)
    lexer = qasm3Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()

    comments = []
    all_tokens = token_stream.getTokens(0, len(token_stream.tokens))

    for token in all_tokens:
        if token.channel == lexer.HIDDEN:
            if token.type == lexer.LineComment:
                comments.append(
                    {
                        "type": "line",
                        "text": token.text,
                        "line": token.line,
                        "column": token.column,
                    }
                )
            elif token.type == lexer.BlockComment:
                comments.append(
                    {
                        "type": "block",
                        "text": token.text,
                        "line": token.line,
                        "column": token.column,
                    }
                )

    return comments


_NodeT = TypeVar("_NodeT", bound=ast.QASMNode)


def add_span(node: _NodeT, span: ast.Span) -> _NodeT:
    """Set the span of a node and return the node"""
    node.span = span
    return node


def combine_span(first: ast.Span, second: ast.Span):
    """Combine two spans and return the combined one"""
    return ast.Span(first.start_line, first.start_column, second.end_line, second.end_column)


def span(func):
    """Function decorator to automatic attach span to nodes for visit* methods."""

    def wrapped(*args, **kwargs):
        span = get_span(args[1])  # args[1] is ctx
        node = func(*args, **kwargs)
        if node is None:
            raise ValueError(f"None encountered at {span}")
        return add_span(node, span)

    return wrapped


def _visit_identifier(identifier: TerminalNode):
    return add_span(ast.Identifier(identifier.getText()), get_span(identifier))  # type: ignore[attr-defined]


def _raise_from_context(ctx: ParserRuleContext, message: str):
    raise QASM3ParsingError(message, ctx.start.line, ctx.start.column)


class QASMNodeVisitor(qasm3ParserVisitor):
    def __init__(self, version: Optional[Tuple[int, ...]] = None, ignore_version: bool = False):
        # A stack of "contexts", each of which is a stack of "scopes".  Contexts
        # are for the main program, gates and subroutines, while scopes are
        # loops, if/else and manual scoping constructs.  Each "context" always
        # contains at least one scope: the base ``ParserRuleContext`` that
        # opened it.
        self._contexts: List[List[ParserRuleContext]] = []
        self._ignore_version = ignore_version
        self._version = _normalize_version(version) if version else None
        self._has_version_declaration = False

    @contextmanager
    def _push_context(self, ctx: ParserRuleContext):
        self._contexts.append([ctx])
        yield
        self._contexts.pop()

    @contextmanager
    def _push_scope(self, ctx: ParserRuleContext):
        self._contexts[-1].append(ctx)
        yield
        self._contexts[-1].pop()

    def _current_context(self):
        return self._contexts[-1]

    def _current_scope(self):
        return self._contexts[-1][-1]

    def _current_base_scope(self):
        return self._contexts[-1][0]

    def _in_global_scope(self):
        return len(self._contexts) == 1 and len(self._contexts[0]) == 1

    def _in_gate(self):
        return isinstance(self._current_base_scope(), qasm3Parser.GateStatementContext)

    def _in_subroutine(self):
        return isinstance(self._current_base_scope(), qasm3Parser.DefStatementContext)

    def _in_loop(self):
        return any(
            isinstance(
                scope,
                (qasm3Parser.ForStatementContext, qasm3Parser.WhileStatementContext),
            )
            for scope in reversed(self._current_context())
        )

    def _check_feature_version(self, ctx, feature_name: str) -> None:
        """Raise when a feature is used below its minimum effective version."""
        if self._ignore_version or self._version is None:
            return
        minimum_version = FEATURE_MIN_VERSION.get(feature_name)
        if minimum_version and self._version < minimum_version:
            version_str = _format_version(self._version)
            minimum_str = _format_version(minimum_version)
            version_source = (
                f"version {version_str} was declared"
                if self._has_version_declaration
                else f"the effective version is {version_str}"
            )
            _raise_from_context(
                ctx,
                f"'{feature_name}' requires OpenQASM {minimum_str} or later, "
                f"but {version_source}",
            )

    def _parse_scoped_statements(
        self, node: Union[qasm3Parser.ScopeContext, qasm3Parser.StatementOrScopeContext]
    ) -> List[ast.Statement]:
        with self._push_scope(node.parentCtx):
            block = self.visit(node)
            return block.statements if isinstance(block, ast.CompoundStatement) else [block]

    @span
    def visitProgram(self, ctx: qasm3Parser.ProgramContext):
        with self._push_context(ctx):
            self._has_version_declaration = ctx.version() is not None
            version = ctx.version().VersionSpecifier().getText() if ctx.version() else None
            statements = [self.visit(statement) for statement in ctx.statementOrScope()]
            return ast.Program(statements=statements, version=version)

    @span
    def visitStatement(self, ctx: qasm3Parser.StatementContext):
        if ctx.pragma():
            return self.visit(ctx.pragma())
        out = self.visit(ctx.getChild(-1))
        out.annotations = [self.visit(annotation) for annotation in ctx.annotation()]
        return out

    @span
    def visitAnnotation(self, ctx: qasm3Parser.AnnotationContext):
        return ast.Annotation(
            keyword=ctx.AnnotationKeyword().getText()[1:],
            command=ctx.RemainingLineContent().getText() if ctx.RemainingLineContent() else None,
        )

    @span
    def visitScope(self, ctx: qasm3Parser.ScopeContext) -> ast.CompoundStatement:
        return ast.CompoundStatement(
            statements=[self.visit(statement) for statement in ctx.statementOrScope()]
        )

    @span
    def visitPragma(self, ctx: qasm3Parser.PragmaContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "pragmas must be global")
        return ast.Pragma(
            command=ctx.RemainingLineContent().getText() if ctx.RemainingLineContent() else ""
        )

    @span
    def visitAliasDeclarationStatement(self, ctx: qasm3Parser.AliasDeclarationStatementContext):
        return ast.AliasStatement(
            target=_visit_identifier(ctx.Identifier()),
            value=self.visit(ctx.aliasExpression()),
        )

    @span
    def visitAssignmentStatement(self, ctx: qasm3Parser.AssignmentStatementContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot assign to classical parameters in a gate")
        measure = ctx.measureExpression() or ctx.quantumCallExpression()
        if measure:
            return ast.QuantumMeasurementStatement(
                measure=self.visit(measure),
                target=self.visit(ctx.indexedIdentifier()),
            )
        return ast.ClassicalAssignment(
            lvalue=self.visit(ctx.indexedIdentifier()),
            op=ast.AssignmentOperator[ctx.op.text],
            rvalue=self.visit(ctx.expression()),
        )

    @span
    def visitBarrierStatement(self, ctx: qasm3Parser.BarrierStatementContext):
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        return ast.QuantumBarrier(qubits=qubits)

    @span
    def visitBoxStatement(self, ctx: qasm3Parser.BoxStatementContext):
        return ast.Box(
            duration=self.visit(ctx.designator()) if ctx.designator() else None,
            body=self._parse_scoped_statements(ctx.scope()),
        )

    @span
    def visitBreakStatement(self, ctx: qasm3Parser.BreakStatementContext):
        if not self._in_loop():
            _raise_from_context(ctx, "'break' statement outside loop")
        return ast.BreakStatement()

    @span
    def visitCalStatement(self, ctx: qasm3Parser.CalStatementContext):
        return ast.CalibrationStatement(
            body=ctx.CalibrationBlock().getText() if ctx.CalibrationBlock() else ""
        )

    @span
    def visitCalibrationGrammarStatement(self, ctx: qasm3Parser.CalibrationGrammarStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "'defcalgrammar' statements must be global")
        return ast.CalibrationGrammarDeclaration(name=ctx.StringLiteral().getText()[1:-1])

    @span
    def visitClassicalDeclarationStatement(
        self, ctx: qasm3Parser.ClassicalDeclarationStatementContext
    ):
        if self._in_gate():
            _raise_from_context(ctx, "cannot declare classical variables in a gate")
        if ctx.arrayType() and not self._in_global_scope():
            _raise_from_context(ctx, "arrays can only be declared globally")
        init = self.visit(ctx.declarationExpression()) if ctx.declarationExpression() else None
        return ast.ClassicalDeclaration(
            type=self.visit(ctx.scalarType() or ctx.arrayType()),
            identifier=_visit_identifier(ctx.Identifier()),
            init_expression=init,
        )

    @span
    def visitConstDeclarationStatement(self, ctx: qasm3Parser.ConstDeclarationStatementContext):
        return ast.ConstantDeclaration(
            type=self.visit(ctx.scalarType()),
            identifier=_visit_identifier(ctx.Identifier()),
            init_expression=self.visit(ctx.declarationExpression()),
        )

    @span
    def visitContinueStatement(self, ctx: qasm3Parser.ContinueStatementContext):
        if not self._in_loop():
            _raise_from_context(ctx, "'continue' statement outside loop")
        return ast.ContinueStatement()

    @span
    def visitDefStatement(self, ctx: qasm3Parser.DefStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "subroutine definitions must be global")
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [self.visit(argument) for argument in ctx.argumentDefinitionList().argumentDefinition()]
            if ctx.argumentDefinitionList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )
        with self._push_context(ctx):
            body = self._parse_scoped_statements(ctx.scope())
        return ast.SubroutineDefinition(
            name=name, arguments=arguments, body=body, return_type=return_type
        )

    @span
    def visitDefcalStatement(self, ctx: qasm3Parser.DefcalStatementContext):
        arguments = (
            [
                self.visit(argument)
                for argument in ctx.defcalArgumentDefinitionList().defcalArgumentDefinition()
            ]
            if ctx.defcalArgumentDefinitionList()
            else []
        )
        qubits = [self.visit(operand) for operand in ctx.defcalOperandList().defcalOperand() or []]
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )

        return ast.CalibrationDefinition(
            name=self.visit(ctx.defcalTarget()),
            arguments=arguments,
            qubits=qubits,
            return_type=return_type,
            body=ctx.CalibrationBlock().getText() if ctx.CalibrationBlock() else "",
        )

    @span
    def visitDelayStatement(self, ctx: qasm3Parser.DelayStatementContext):
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        return ast.DelayInstruction(duration=self.visit(ctx.designator()), qubits=qubits)

    @span
    def visitEndStatement(self, _: qasm3Parser.EndStatementContext):
        return ast.EndStatement()

    @span
    def visitExpressionStatement(self, ctx: qasm3Parser.ExpressionStatementContext):
        return ast.ExpressionStatement(self.visit(ctx.expression()))

    @span
    def visitExternStatement(self, ctx: qasm3Parser.ExternStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "extern declarations must be global")
        arguments = (
            [self.visit(type) for type in ctx.externArgumentList().externArgument()]
            if ctx.externArgumentList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )
        return ast.ExternDeclaration(
            name=_visit_identifier(ctx.Identifier()),
            arguments=arguments,
            return_type=return_type,
        )

    @span
    def visitForStatement(self, ctx: qasm3Parser.ForStatementContext):
        if ctx.setExpression():
            set_declaration = self.visit(ctx.setExpression())
        elif ctx.rangeExpression():
            set_declaration = self.visit(ctx.rangeExpression())
        else:
            set_declaration = self.visit(ctx.expression())
        block = self._parse_scoped_statements(ctx.body)
        return ast.ForInLoop(
            type=self.visit(ctx.scalarType()),
            identifier=_visit_identifier(ctx.Identifier()),
            set_declaration=set_declaration,
            block=block,
        )

    @span
    def visitGateCallStatement(self, ctx: qasm3Parser.GateCallStatementContext):
        modifiers = [self.visit(modifier) for modifier in ctx.gateModifier()]
        arguments = (
            [self.visit(argument) for argument in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        if ctx.GPHASE():
            if len(arguments) != 1:
                _raise_from_context(
                    ctx,
                    f"'gphase' takes exactly one argument, but received {arguments}",
                )
            return ast.QuantumPhase(modifiers=modifiers, argument=arguments[0], qubits=qubits)
        return ast.QuantumGate(
            modifiers=modifiers,
            name=_visit_identifier(ctx.Identifier()),
            arguments=arguments,
            qubits=qubits,
            duration=self.visit(ctx.designator()) if ctx.designator() else None,
        )

    @span
    def visitGateStatement(self, ctx: qasm3Parser.GateStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "gate definitions must be global")
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [_visit_identifier(id_) for id_ in ctx.params.Identifier()]
            if ctx.params is not None
            else []
        )
        qubits = [_visit_identifier(id_) for id_ in ctx.qubits.Identifier()]
        with self._push_context(ctx):
            body = cast(List[ast.QuantumStatement], self._parse_scoped_statements(ctx.scope()))
        return ast.QuantumGateDefinition(name, arguments, qubits, body)

    @span
    def visitIfStatement(self, ctx: qasm3Parser.IfStatementContext):
        if_body = self._parse_scoped_statements(ctx.if_body)
        else_body = self._parse_scoped_statements(ctx.else_body) if ctx.else_body else []
        return ast.BranchingStatement(
            condition=self.visit(ctx.expression()),
            if_block=if_body,
            else_block=else_body,
        )

    @span
    def visitIncludeStatement(self, ctx: qasm3Parser.IncludeStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "'include' statements must be global")
        return ast.Include(target=ctx.StringLiteral().getText()[1:-1])

    @span
    def visitIoDeclarationStatement(self, ctx: qasm3Parser.IoDeclarationStatementContext):
        if not self._in_global_scope():
            keyword = "input" if ctx.INPUT() else "output"
            _raise_from_context(ctx, f"'{keyword}' declarations must be global")
        return ast.IODeclaration(
            io_identifier=ast.IOKeyword.input if ctx.INPUT() else ast.IOKeyword.output,
            type=self.visit(ctx.scalarType() or ctx.arrayType()),
            identifier=_visit_identifier(ctx.Identifier()),
        )

    @span
    def visitNopStatement(self, ctx: qasm3Parser.NopStatementContext):
        self._check_feature_version(ctx, "nop")
        if (operands := ctx.gateOperandList()) is None:
            return ast.QuantumNop(operands=[])
        return ast.QuantumNop(operands=[self.visit(operand) for operand in operands.gateOperand()])

    @span
    def visitMeasureArrowAssignmentStatement(
        self, ctx: qasm3Parser.MeasureArrowAssignmentStatementContext
    ):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'measure' instruction in a gate")
        measure = ctx.measureExpression() or ctx.quantumCallExpression()
        return ast.QuantumMeasurementStatement(
            measure=self.visit(measure),
            target=self.visit(ctx.indexedIdentifier()) if ctx.indexedIdentifier() else None,
        )

    @span
    def visitOldStyleDeclarationStatement(
        self, ctx: qasm3Parser.OldStyleDeclarationStatementContext
    ):
        identifier = _visit_identifier(ctx.Identifier())
        size = self.visit(ctx.designator()) if ctx.designator() else None
        if isinstance(size, ast.UnaryExpression) or (
            isinstance(size, ast.IntegerLiteral) and size.value == 0
        ):
            _raise_from_context(
                ctx.designator(),
                ("qreg" if ctx.QREG() else "creg") + " size must be positive",
            )
        if ctx.QREG():
            if not self._in_global_scope():
                _raise_from_context(ctx, "qubit declarations must be global")
            return ast.QubitDeclaration(qubit=identifier, size=size)
        span = (
            combine_span(get_span(ctx.CREG()), get_span(ctx.designator()))
            if ctx.designator()
            else get_span(ctx.CREG())
        )
        return ast.ClassicalDeclaration(
            type=add_span(ast.BitType(size=size), span),
            identifier=identifier,
            init_expression=None,
        )

    @span
    def visitQuantumDeclarationStatement(self, ctx: qasm3Parser.QuantumDeclarationStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "qubit declarations must be global")
        size_designator = ctx.qubitType().designator()
        return ast.QubitDeclaration(
            qubit=_visit_identifier(ctx.Identifier()),
            size=self.visit(size_designator) if size_designator is not None else None,
        )

    @span
    def visitResetStatement(self, ctx: qasm3Parser.ResetStatementContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'reset' instruction in a gate")
        return ast.QuantumReset(qubits=self.visit(ctx.gateOperand()))

    @span
    def visitReturnStatement(self, ctx: qasm3Parser.ReturnStatementContext):
        if not self._in_subroutine():
            _raise_from_context(ctx, "'return' statement outside subroutine")
        if ctx.expression():
            expression = self.visit(ctx.expression())
        elif ctx.measureExpression():
            expression = self.visit(ctx.measureExpression())
        elif ctx.quantumCallExpression():
            expression = self.visit(ctx.quantumCallExpression())
        else:
            expression = None
        return ast.ReturnStatement(expression=expression)

    @span
    def visitSwitchStatement(self, ctx: qasm3Parser.SwitchStatementContext):
        self._check_feature_version(ctx, "switch")
        target = self.visit(ctx.expression())
        cases = []
        default = None
        for case in ctx.switchCaseItem():
            if case.CASE():
                if default is not None:
                    _raise_from_context(case, "'case' statement after 'default'")
                values = []
                for expr in case.expressionList().expression():
                    # This AST-generation step does not perform constant folding to validate that
                    # only distinct integers are encountered; we leave that to a later step.
                    values.append(self.visit(expr))
                cases.append((values, self.visit(case.scope())))
            elif default is not None:
                _raise_from_context(case, "multiple 'default' cases")
            else:
                default = self.visit(case.scope())
        return ast.SwitchStatement(target=target, cases=cases, default=default)

    @span
    def visitWhileStatement(self, ctx: qasm3Parser.WhileStatementContext):
        block = self._parse_scoped_statements(ctx.body)
        return ast.WhileLoop(while_condition=self.visit(ctx.expression()), block=block)

    @span
    def visitParenthesisExpression(self, ctx: qasm3Parser.ParenthesisExpressionContext):
        return self.visit(ctx.expression())

    @span
    def visitIndexExpression(self, ctx: qasm3Parser.IndexExpressionContext):
        return ast.IndexExpression(
            collection=self.visit(ctx.expression()),
            index=self.visit(ctx.indexOperator()),
        )

    @span
    def visitUnaryExpression(self, ctx: qasm3Parser.UnaryExpressionContext):
        return ast.UnaryExpression(
            op=ast.UnaryOperator[ctx.op.text],
            expression=self.visit(ctx.expression()),
        )

    @span
    def _visit_binary_expression(self, ctx: _BinaryExpressionContext):
        return ast.BinaryExpression(
            lhs=self.visit(ctx.expression(0)),
            op=ast.BinaryOperator[ctx.op.text],
            rhs=self.visit(ctx.expression(1)),
        )

    visitPowerExpression = _visit_binary_expression
    visitMultiplicativeExpression = _visit_binary_expression
    visitAdditiveExpression = _visit_binary_expression
    visitBitshiftExpression = _visit_binary_expression
    visitComparisonExpression = _visit_binary_expression
    visitEqualityExpression = _visit_binary_expression
    visitBitwiseAndExpression = _visit_binary_expression
    visitBitwiseXorExpression = _visit_binary_expression
    visitBitwiseOrExpression = _visit_binary_expression
    visitLogicalAndExpression = _visit_binary_expression
    visitLogicalOrExpression = _visit_binary_expression

    @span
    def visitCastExpression(self, ctx: qasm3Parser.CastExpressionContext):
        return ast.Cast(type=self.visit(ctx.getChild(0)), argument=self.visit(ctx.expression()))

    @span
    def visitMeasureExpression(self, ctx: qasm3Parser.MeasureExpressionContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'measure' instruction in a gate")
        return ast.QuantumMeasurement(qubit=self.visit(ctx.gateOperand()))

    @span
    def visitQuantumCallExpression(self, ctx: qasm3Parser.QuantumCallExpressionContext):
        if self._in_gate():
            _raise_from_context(
                ctx,
                "cannot have a non-unitary measure-like quantum call expression instruction in a gate",
            )
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [self.visit(argument) for argument in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        return ast.QuantumCallExpression(
            name=name,
            arguments=arguments,
            qubits=[self.visit(operand) for operand in ctx.gateOperandList().gateOperand()],
        )

    @span
    def visitDurationofExpression(self, ctx: qasm3Parser.DurationofExpressionContext):
        target = self._parse_scoped_statements(ctx.scope())
        return ast.DurationOf(target=target)

    @span
    def visitCallExpression(self, ctx: qasm3Parser.CallExpressionContext):
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [self.visit(argument) for argument in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        if name.name == "sizeof":
            if len(arguments) not in (1, 2):
                _raise_from_context(ctx, "'sizeof' needs either one or two arguments")
            return ast.SizeOf(
                target=arguments[0],
                index=arguments[1] if len(arguments) == 2 else None,
            )
        return ast.FunctionCall(name=name, arguments=arguments)

    @span
    def visitLiteralExpression(self, ctx: qasm3Parser.LiteralExpressionContext):
        if ctx.Identifier():
            return _visit_identifier(ctx.Identifier())
        if ctx.BinaryIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.BinaryIntegerLiteral().getText(), 2))
        if ctx.OctalIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.OctalIntegerLiteral().getText(), 8))
        if ctx.DecimalIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.DecimalIntegerLiteral().getText(), 10))
        if ctx.HexIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.HexIntegerLiteral().getText(), 16))
        if ctx.FloatLiteral():
            return ast.FloatLiteral(value=float(ctx.FloatLiteral().getText()))
        if ctx.ImaginaryLiteral():
            return ast.ImaginaryLiteral(value=float(ctx.ImaginaryLiteral().getText()[:-2]))
        if ctx.BooleanLiteral():
            return ast.BooleanLiteral(value=ctx.BooleanLiteral().getText() == "true")
        if ctx.BitstringLiteral():
            stripped = ctx.BitstringLiteral().getText()[1:-1].replace("_", "")
            return ast.BitstringLiteral(value=int(stripped, 2), width=len(stripped))
        if ctx.TimingLiteral():
            text = ctx.TimingLiteral().getText()
            value, suffix = text[:-2], text[-2:]
            if suffix[1] == "s":
                if suffix[0] in "num":
                    unit = ast.TimeUnit[suffix]
                elif suffix[0] == "µ":
                    unit = ast.TimeUnit["us"]
                else:
                    unit = ast.TimeUnit["s"]
                    value = text[:-1]
            else:
                unit = ast.TimeUnit["dt"]
            return ast.DurationLiteral(value=float(value), unit=unit)
        if ctx.HardwareQubit():
            return ast.Identifier(ctx.HardwareQubit().getText())
        raise _raise_from_context(ctx, "unknown literal type")

    @span
    def visitAliasExpression(self, ctx: qasm3Parser.AliasExpressionContext):
        # This choice in the recursion and the accompanying reversal of the
        # iterator builds the tree as left-associative.  The logical operation
        # is arbitrarily associative, but the AST needs us to make a choice.
        def recurse(previous, iterator):
            rhs = self.visit(previous)
            try:
                current = next(iterator)
            except StopIteration:
                return self.visit(previous)
            lhs = recurse(current, iterator)
            return add_span(ast.Concatenation(lhs=lhs, rhs=rhs), combine_span(lhs.span, rhs.span))

        # This iterator should always be non-empty if ANTLR did its job right.
        iterator = reversed(ctx.expression())
        return recurse(next(iterator), iterator)

    @span
    def visitDeclarationExpression(self, ctx: qasm3Parser.DeclarationExpressionContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitRangeExpression(self, ctx: qasm3Parser.RangeExpressionContext):
        # start, end and step are all optional as in [:]
        # It could be [start:end] or [start:step:end]
        start = None
        end = None
        step = None
        colons_seen = 0

        for child in ctx.getChildren():
            if isinstance(child, qasm3Parser.ExpressionContext):
                expression = self.visit(child)
                if colons_seen == 0:
                    start = expression
                elif colons_seen == 1:
                    end = expression
                else:
                    step = end
                    end = expression
            elif child.getText() == ":":
                colons_seen += 1

        return ast.RangeDefinition(start=start, end=end, step=step)

    @span
    def visitSetExpression(self, ctx: qasm3Parser.SetExpressionContext):
        return ast.DiscreteSet(values=[self.visit(expression) for expression in ctx.expression()])

    @span
    def visitArrayLiteral(self, ctx: qasm3Parser.ArrayLiteralContext):
        array_literal_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.ArrayLiteralContext,
        )

        def predicate(child):
            return isinstance(child, array_literal_element)

        return ast.ArrayLiteral(
            values=[self.visit(element) for element in ctx.getChildren(predicate=predicate)],
        )

    def visitIndexOperator(self, ctx: qasm3Parser.IndexOperatorContext):
        if ctx.setExpression():
            return self.visit(ctx.setExpression())

        index_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.RangeExpressionContext,
        )

        def predicate(child):
            return isinstance(child, index_element)

        return [self.visit(child) for child in ctx.getChildren(predicate=predicate)]

    @span
    def visitIndexedIdentifier(self, ctx: qasm3Parser.IndexedIdentifierContext):
        if not ctx.indexOperator():
            return _visit_identifier(ctx.Identifier())
        return ast.IndexedIdentifier(
            name=_visit_identifier(ctx.Identifier()),
            indices=[self.visit(index) for index in ctx.indexOperator()],
        )

    @span
    def visitDesignator(self, ctx: qasm3Parser.DesignatorContext):
        return self.visit(ctx.expression())

    @span
    def visitGateModifier(self, ctx: qasm3Parser.GateModifierContext):
        if ctx.INV():
            return ast.QuantumGateModifier(modifier=ast.GateModifierName["inv"], argument=None)
        if ctx.POW():
            return ast.QuantumGateModifier(
                modifier=ast.GateModifierName["pow"],
                argument=self.visit(ctx.expression()),
            )
        return ast.QuantumGateModifier(
            modifier=ast.GateModifierName["ctrl" if ctx.CTRL() else "negctrl"],
            argument=self.visit(ctx.expression()) if ctx.expression() else None,
        )

    @span
    def visitScalarType(self, ctx: qasm3Parser.ScalarTypeContext):
        if ctx.BOOL():
            return ast.BoolType()
        if ctx.DURATION():
            return ast.DurationType()
        if ctx.STRETCH():
            return ast.StretchType()
        if ctx.BIT():
            return ast.BitType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.INT():
            designator = ctx.designator()
            size = self.visit(designator) if designator else None
            if isinstance(size, ast.UnaryExpression) or (
                isinstance(size, ast.IntegerLiteral) and size.value == 0
            ):
                _raise_from_context(designator, "int size must be positive")
            return ast.IntType(size=size)
        if ctx.UINT():
            designator = ctx.designator()
            size = self.visit(designator) if designator else None
            if isinstance(size, ast.UnaryExpression) or (
                isinstance(size, ast.IntegerLiteral) and size.value == 0
            ):
                _raise_from_context(designator, "uint size must be positive")
            return ast.UintType(size=size)
        if ctx.FLOAT():
            return ast.FloatType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.ANGLE():
            designator = ctx.designator()
            size = self.visit(designator) if designator else None
            if isinstance(size, ast.UnaryExpression) or (
                isinstance(size, ast.IntegerLiteral) and size.value == 0
            ):
                _raise_from_context(designator, "angle size must be positive")
            return ast.AngleType(size=size)
        if ctx.COMPLEX():
            base = self.visit(ctx.scalarType()) if ctx.scalarType() else None
            if base is not None and not isinstance(base, ast.FloatType):
                _raise_from_context(ctx.scalarType(), f"invalid type of complex components")
            return ast.ComplexType(base_type=base)
        _raise_from_context(ctx, "unhandled type: {ctx.getText()}")

    @span
    def visitArrayType(self, ctx: qasm3Parser.ArrayTypeContext):
        base = self.visit(ctx.scalarType())
        if not isinstance(
            base,
            (
                ast.BitType,
                ast.IntType,
                ast.UintType,
                ast.FloatType,
                ast.AngleType,
                ast.DurationType,
                ast.BoolType,
                ast.ComplexType,
            ),
        ):
            _raise_from_context(ctx.scalarType(), f"invalid scalar type for array")
        dimensions: list = []
        for expression in ctx.expressionList().expression():
            dimensions.append(self.visit(expression))
            if isinstance(dimensions[-1], ast.UnaryExpression):
                _raise_from_context(expression, f"all array dimensions must be non-negative")
        return ast.ArrayType(
            base_type=base,
            dimensions=dimensions,
        )

    @span
    def visitGateOperand(self, ctx: qasm3Parser.GateOperandContext):
        if ctx.HardwareQubit():
            return ast.Identifier(name=ctx.getText())
        return self.visit(ctx.indexedIdentifier())

    @span
    def visitDefcalTarget(self, ctx: qasm3Parser.DefcalTargetContext):
        return ast.Identifier(name=ctx.getText())

    @span
    def visitArgumentDefinition(self, ctx: qasm3Parser.ArgumentDefinitionContext):
        name = _visit_identifier(ctx.Identifier())
        if ctx.qubitType() or ctx.QREG():
            designator = ctx.qubitType().designator() if ctx.qubitType() else ctx.designator()
            return ast.QuantumArgument(
                name=name, size=self.visit(designator) if designator else None
            )
        access = None
        type_: ast.ClassicalType
        if ctx.CREG():
            size = self.visit(ctx.designator()) if ctx.designator() else None
            creg_span = get_span(ctx.CREG())
            type_ = add_span(
                ast.BitType(size=size),
                combine_span(creg_span, get_span(size)) if size else creg_span,
            )
        elif ctx.arrayReferenceType():
            array_ctx = ctx.arrayReferenceType()
            access = (
                ast.AccessControl.readonly if array_ctx.READONLY() else ast.AccessControl.mutable
            )
            base_type = self.visit(array_ctx.scalarType())
            dimensions = (
                self.visit(array_ctx.expression())
                if array_ctx.expression()
                else [self.visit(expr) for expr in array_ctx.expressionList().expression()]
            )
            type_ = add_span(
                ast.ArrayReferenceType(base_type=base_type, dimensions=dimensions),
                get_span(array_ctx),
            )
        else:
            type_ = self.visit(ctx.scalarType())
        return ast.ClassicalArgument(type=type_, name=name, access=access)

    @span
    def visitDefcalArgumentDefinition(self, ctx: qasm3Parser.DefcalArgumentDefinitionContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitExternArgument(self, ctx: qasm3Parser.ExternArgumentContext):
        access = None
        type_: ast.ClassicalType
        if ctx.CREG():
            type_ = ast.BitType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        elif ctx.scalarType():
            type_ = self.visit(ctx.scalarType())
        else:
            array_ctx = ctx.arrayReferenceType()
            access = (
                ast.AccessControl.readonly if array_ctx.READONLY() else ast.AccessControl.mutable
            )
            base_type = self.visit(array_ctx.scalarType())
            dimensions = (
                self.visit(array_ctx.expression())
                if array_ctx.expression()
                else [self.visit(expr) for expr in array_ctx.expressionList().expression()]
            )
            type_ = add_span(
                ast.ArrayReferenceType(base_type=base_type, dimensions=dimensions),
                get_span(array_ctx),
            )
        return ast.ExternArgument(type=type_, access=access)

    @span
    def visitDefcalOperand(self, ctx: qasm3Parser.DefcalOperandContext):
        if ctx.HardwareQubit():
            return ast.Identifier(ctx.HardwareQubit().getText())
        return _visit_identifier(ctx.Identifier())

    def visitStatementOrScope(self, ctx: qasm3Parser.StatementOrScopeContext) -> ast.Statement:
        """Visit one ``statementOrScope``, version-gating a braces block used as a statement.

        ``{...}`` as the body of ``if``, ``for`` or ``while`` has been legal since 3.0, whereas
        ``{...}`` standing where a statement is expected is the anonymous scope that 3.1
        introduced.  Both parse to the same ``scope`` rule, so only the parent separates them.
        """
        # Only the `scope` alternative can be a bare block; `statement` never is.
        if ctx.scope():
            # `program` and `scope` are the only rules with a `statementOrScope*` list, so a block
            # reached from either fills a statement slot and is anonymous, even when that list is
            # itself some construct's body.  The other three parents, `for`, `if` and `while`,
            # arrive through a single `body=`/`if_body=`/`else_body=`, where the block *is* the
            # body.  `box`, `def`, `gate`, `durationof` and `switch` case/default take `scope`
            # directly instead of through `statementOrScope`, so they never reach this method.
            parent = ctx.parentCtx
            if isinstance(parent, (qasm3Parser.ProgramContext, qasm3Parser.ScopeContext)):
                self._check_feature_version(ctx, "anonymous_scope")
            return self.visit(ctx.scope())
        return self.visit(ctx.statement())
