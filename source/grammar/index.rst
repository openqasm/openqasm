OpenQasm 3.0 Grammar
====================

OpenQasm 3.0 Grammar specification based in ANTLR_ parser generator.

The ANTLR grammar is intended to serve as the official reference grammar for OpenQASM3 and defines
the set of syntactically valid statements in the language. ANTLR is used because it provides a
human-readable EBNF format that is computer-validatable. It provides an auto-generated parser that is
used to validate the example files (see `openqasm/examples/`). As an extension, it can be used
to check whether a source file is parseable OpenQASM3 (note this does not ensure that the OpenQASM3 is semantically correct).

The ANTLR parser does not attempt to be performant or construct
an AST. Furthermore, it does not conduct any semantic analysis.

The ANTLR grammar may serve as a guide when developing compiler tooling for OpenQASM3.

.. _ANTLR: https://www.antlr.org/

.. literalinclude:: qasm3.g4
   :language: antlr
   :linenos:
