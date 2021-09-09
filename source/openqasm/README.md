# OpenNode: a reference OpenQASM 3.0 AST in Python

This directory contains a reference AST implementation for OpenQASM 3.0 in Python. It consists of:

* ast.py: The AST nodes.
* parser/antlr: A parser based on Antlr grammar and reference parser also found in this repo.
It walks the ANTLR parse tree to generate the AST tree.
* ast_visitor: A base AST visitor and an example showing how to implement compiler passes
using the visitor.
* tests: A set of unit tests.


## Developer setup

1. Setup the Antlr tools following the [README under grammar](../README.md). Then from 
source/grammar directory, run:
```
antlr4 -o ../openqasm/parser/antlr -Dlanguage=Python3 -visitor qasm3.g4
```
2. Change to the current directory and install additional requirements with 
`pip install -r requirements.txt -r requirements-dev.txt`.
3. Format python code: `black .`.
4. Check style: `bylint .`.
5. Run tests: `pytest`.
