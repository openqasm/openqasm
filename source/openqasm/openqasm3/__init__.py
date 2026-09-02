"""
===================================
OpenQASM 3 Python reference package
===================================

This package contains the reference abstract syntax tree (AST) for representing
OpenQASM 3 programs, tools to parse text into this AST, and tools to manipulate
the AST.

The AST itself is in the :obj:`.ast` module.  There is a reference parser in the
:obj:`.parser` module, which requires the ``[parser]`` extra to be installed.

With the ``[parser]`` extra installed, the simplest interface to the parser is
the :obj:`~parser.parse` function.  You can use :func:`.parse_version` to check
the potential version of an OpenQASM program before invoking your own parser.

By default the parser does not resolve ``include`` statements and performs no
file-system access.  Pass ``includes=`` to :func:`.parse` to enable resolution.
Raw source backends create an unscoped environment; pass an
:class:`.IncludeEnvironment` to bind source lookup and scoped library names
atomically.  See the :obj:`.resolver` module for the complete interface.
"""

__all__ = [
    "ast",
    "visitor",
    "properties",
    "spec",
    "resolver",
    "dump",
    "dumps",
    "parser",
    "parse",
    "parse_version",
    "IncludeEnvironment",
    "IncludeResolver",
    "DictResolver",
    "FunctionResolver",
    "ChoiceResolver",
    "StandardLibraryResolver",
    "ResolvedSource",
    "IncludeSource",
    "flatten_includes",
    "as_resolver",
    "library_root",
    "library_name",
    "validate_source_identity",
    "validate_library_name",
    "validate_include_target",
    "STANDARD_LIBRARY_NAME",
    "LIBRARY_PREFIX",
    "ROOT_RELATIVE_PREFIX",
    "MINIMUM_INCLUDE_DEPTH",
    "DEFAULT_MAX_INCLUDE_DEPTH",
    "IncludeError",
    "IncludeNotFoundError",
    "CyclicIncludeError",
    "IncludeDepthExceededError",
    "InvalidIncludeTargetError",
    "AmbiguousIncludeTargetError",
    "InconsistentResolutionError",
]

__version__ = "1.0.1"

from . import ast, visitor, properties, spec, resolver

from .printer import dump, dumps
from .resolver import (
    AmbiguousIncludeTargetError,
    InconsistentResolutionError,
    ChoiceResolver,
    CyclicIncludeError,
    DictResolver,
    FunctionResolver,
    IncludeDepthExceededError,
    IncludeEnvironment,
    IncludeError,
    IncludeNotFoundError,
    IncludeResolver,
    InvalidIncludeTargetError,
    IncludeSource,
    ResolvedSource,
    StandardLibraryResolver,
    as_resolver,
    flatten_includes,
    library_name,
    library_root,
    validate_library_name,
    validate_source_identity,
    validate_include_target,
    STANDARD_LIBRARY_NAME,
    LIBRARY_PREFIX,
    ROOT_RELATIVE_PREFIX,
    MINIMUM_INCLUDE_DEPTH,
    DEFAULT_MAX_INCLUDE_DEPTH,
)

# Try to initialise the 'parsing' extra components.
try:
    import antlr4
except ModuleNotFoundError:
    pass
else:
    # Any import errors in section are of interest to the user, and should be propagated.
    del antlr4
    from . import parser
    from .parser import parse, parse_version
