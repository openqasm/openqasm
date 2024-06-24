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
the :obj:`~parser.parse` function.
"""

__all__ = [
    "ast",
    "visitor",
    "properties",
    "spec",
    "dump",
    "dumps",
    "parser",
    "parse",
]

__version__ = "1.0.0"

from . import ast, visitor, properties, spec

from .printer import dump, dumps

# Try to initialise the 'parsing' extra components.
try:
    import antlr4
except ModuleNotFoundError:
    pass
else:
    # Any import errors in section are of interest to the user, and should be propagated.
    del antlr4
    from . import parser
    from .parser import parse
