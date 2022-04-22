# OpenPulse Python Reference

[![License](https://img.shields.io/github/license/Qiskit/openqasm.svg)](https://opensource.org/licenses/Apache-2.0)<!-- long-description-skip-begin -->[![Release](https://img.shields.io/pypi/v/openqasm3)](https://pypi.org/project/openqasm3)<!-- long-description-skip-end -->

The `openpulse` package contains the reference abstract syntax tree (AST) for representing OpenPulse programs, tools to parse text into this AST, and tools to manipulate the AST.

The AST is intended to help with writing compiler passes for OpenPulse in Python. OpenPulse is a minor extension on
OpenQASM 3 with additional types to describe pulse.
It aims to have no dependencies for users who consume the Python tree structure, and minimal dependencies for parsing a string to this tree structure.
The AST is simpler than a Concrete Syntax Tree (CST) which preserves comments, spacing, etc for use by editor plugins.

The package consists of the modules:

* `openpulse.ast`: The AST nodes.

* `openpulse.parser`:
  A parser based on an ANTLR grammar and reference parser also found in this repo.
  It walks the ANTLR parse tree to generate the AST.

* `tests`: A set of unit tests.


**Note**: this reference Python package is currently in the early stages of development, and _no_ parts of the API should be considered stable at this time.
The AST itself will be subject to change in backwards-incompatible ways, mirroring the development of the OpenQASM 3 language itself.


## Installation

The package can be installed from PyPI (`pip`) with the command

```bash
python -m pip install openpulse
```

If you want to use the parser, you will need to install the extra `parsing`, and to run the tests you need the extra `tests`, for example `pip install openpulse[tests]`.
All extras can be installed with the target `openpulse[all]`.


## Development Environment

To work on development, you will need to first follow the README in openqasm directory and install openqasm3 to your
virtual environment. One way is from the openqasm directory,
run:

```bash
python -m pip install -e .
```

### Developer tools

This package uses the same developer tools as openqasm.
