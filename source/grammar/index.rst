OpenQasm 3.0 Grammar
====================

OpenQasm 3.0 Grammar specification based in ANTLR_ parser generator.

The ANTLR grammar is intended to serve as the official reference grammar for OpenQASM3 and defines
the set of syntactically valid statements in the language. ANTLR is used because it provides a
human readable EBNF format which can evolve quickly. It further enables validation of the example
files (see `openqasm/examples/`) via the built-in ANTLR parser. As an extension, it can be used
to check whether a block of code is valid OpenQASM3.

It should be noted, however, that the ANTLR grammar (and the associated parser) are not
intended to be used in production. The ANTLR parser does not attempt to be performant or construct
an AST. Furthermore, it does not conduct any semantic analysis.

Thus, the ANTLR grammar should serve as a guide when developing compiler tooling for OpenQASM3, but
should not itself be used as an OpenQASM parser.

.. _ANTLR: https://www.antlr.org/

.. literalinclude:: qasm3.g4
   :language: antlr
   :linenos:
