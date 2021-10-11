# OpenQASM 3 Python Reference

[![License](https://img.shields.io/github/license/Qiskit/openqasm.svg)](https://opensource.org/licenses/Apache-2.0)<!-- long-description-skip-begin -->[![Release](https://img.shields.io/pypi/v/openqasm3)](https://pypi.org/project/openqasm3)<!-- long-description-skip-end -->

The `openqasm3` package contains the reference abstract syntax tree (AST) for representing OpenQASM 3 programs, tools to parse text into this AST, and tools to manipulate the AST.

The AST is intended to help with writing compiler passes for OpenQASM 3 in Python.
It aims to have no dependencies for users who consume the Python tree structure, and minimal dependencies for parsing a string to this tree structure.
The AST is simpler than a Concrete Syntax Tree (CST) which preserves comments, spacing, etc for use by editor plugins.

The package consists of the modules:

* `openqasm3.ast`: The AST nodes.

* `openqasm3.parser`:
  A parser based on an ANTLR grammar and reference parser also found in this repo.
  It walks the ANTLR parse tree to generate the AST.

* `openqasm3.visitor`: A base AST visitor and transformer.

* `tests`: A set of unit tests.


**Note**: this reference Python package is currently in the early stages of development, and _no_ parts of the API should be considered stable at this time.
The AST itself will be subject to change in backwards-incompatible ways, mirroring the development of the OpenQASM 3 languge itself.


## Installation

The package can be installed from PyPI (`pip`) with the command

```bash
python -m pip install openqasm3
```

If you want to use the parser, you will need to install the extra `parsing`, and to run the tests you need the extra `tests`, for example `pip install openqasm3[tests]`.
All extras can be installed with the target `openqasm3[all]`.


## Development Environment

To work on development, you will need to have a complete [ANTLR](https://www.antlr.org/) installation (not just the runtime), and the ANTLR grammar files from the [main OpenQASM repository](https://github.com/Qiskit/openqasm).

### Setting up ANTLR

You can most likely get a copy of ANTLR using your system package manager if you are on Linux, or from [Homebrew](https://brew.sh) (`brew`) on macOS.
Otherwise, you can follow [these instructions](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).
Make a note of the exact version of ANTLR you have installed, because you will need to ensure your version of `antlr4-python3-runtime` matches exactly.
The package in its current form expects ANTLR 4.9.2.

Once you have ANTLR installed, change to the directory where the `qasm3.g4` file is located (for example, `openqasm/source/grammar`), and run
```bash
<antlr command> -o /path/to/openqasm3/antlr -Dlanguage=Python3 -visitor qasm3.g4
```

For example, if this repository is cloned to `~/openqasm` and the command to run ANTLR is `antlr4`, then you should run
```bash
cd ~/openqasm/source/grammar
antlr4 -o ~/openqasm/source/openqasm/openqasm3/antlr -Dlanguage=Python3 -visitor qasm3.g4
```

### Developer tools

Install the rest of the Python development environment with
```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```
ensuring that the version of `antlr4-python3-runtime` exactly matches the version of ANTLR you have.

Install the Python package in editable mode with
```bash
python -m pip install -e .
```

The project is configured to use the code formatter [`black`](https://pypi.org/project/black), linter [`pylint`](https://pylint.org) and tester [`pytest`](https://pytest.org).
The commands to run these are, respectively:
```bash
black .
pylint .
pytest
```
