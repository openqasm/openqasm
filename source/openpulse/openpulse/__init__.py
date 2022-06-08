"""
===================================
OpenPulse Python reference package
===================================

This package contains the reference abstract syntax tree (AST) for representing
OpenPulse 3 programs, tools to parse text into this AST, and tools to manipulate
the AST.

The AST itself is in the :obj:`.ast` module.  There is a reference parser in the
:obj:`.parser` module, which requires the ``[parser]`` extra to be installed.

With the ``[parser]`` extra installed, the simplest interface to the parser is
the :obj:`~parser.parse` function.
"""

__version__ = "0.0.1"

from . import ast

try:
    from . import parser
    from .parser import parse
except ImportError:
    # Installed without the parsing extra.
    pass
