# A reference OpenQASM 3.0 AST in Python

This Abstract Syntax Tree (AST) is intended to help with writing compiler passes for OpenQASM 3.0 in
Python. It aims to have no dependencies for users who consume the Python tree structure, and minimal
dependencies for parsing a string to this tree structure. The AST is simpler than a Concrete Syntax
Tree (CST) which preserves comments, spacing, etc for use by editor plugins.

This directory consists of:

* ast.py: The AST nodes.
* parser/antlr: A parser based on Antlr grammar and reference parser also found in this repo.
  It walks the ANTLR parse tree to generate the AST.
* visitor.py: A base AST visitor and transformer.
* tests: A set of unit tests.

## Developer setup

1. Setup the Antlr tools following the [README under grammar](../grammar/README.md). Then from 
source/grammar directory, run:
```
antlr4 -o ../openqasm/parser/antlr -Dlanguage=Python3 -visitor qasm3.g4
```
2. Change to the current directory and install additional requirements with 
`pip install -r requirements.txt -r requirements-dev.txt`.
3. Format python code: `black .`.
4. Check style: `pylint .`.
5. Run tests: `pytest`.
