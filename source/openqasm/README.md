# OpenQASM 3 Python Reference

[![License](https://img.shields.io/github/license/openqasm/openqasm.svg)](https://opensource.org/licenses/Apache-2.0)<!-- long-description-skip-begin -->[![Release](https://img.shields.io/pypi/v/openqasm3)](https://pypi.org/project/openqasm3)<!-- long-description-skip-end -->

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

If you want to use the parser, you will need to install the extra `parser`, and to run the tests you need the extra `tests`, for example `pip install openqasm3[tests]`.
All extras can be installed with the target `openqasm3[all]`.


## Development Environment

To work on development, you will need to have a complete [ANTLR](https://www.antlr.org/) installation (not just the runtime), and the ANTLR grammar files from the [main OpenQASM repository](https://github.com/openqasm/openqasm).

### Setting up ANTLR

You can most likely get a copy of ANTLR using your system package manager if you are on Linux, or from [Homebrew](https://brew.sh) (`brew`) on macOS.
Otherwise, you can follow [these instructions](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).
Make a note of the version of ANTLR you have installed, because you will need to ensure your version of `antlr4-python3-runtime` matches up to the minor version.

Once you have ANTLR installed, change to the directory where the `qasm3*.g4` files are located (for example, `repo_root/source/grammar`), and run
```bash
<antlr command> -o <path to here>/openqasm3/_antlr/_<major>_<minor> -Dlanguage=Python3 -visitor qasm3Lexer.g4 qasm3Parser.g4
```

For example, if this repository is cloned to `~/openqasm` and the command to run ANTLR 4.11.1 is `antlr4`, then you should run
```bash
cd ~/openqasm/source/grammar
antlr4 -o ~/openqasm/source/openqasm/openqasm3/_antlr/_4_11 -Dlanguage=Python3 -visitor qasm3Lexer.g4 qasm3Parser.g4
```

You can install more than one version of the ANTLR files at once, provided you put them in the correct version directories.
The package will dynamically choose the correct version based on the installed version of `antlr4_python3_runtime` when it is imported.

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


### Deployment procedure

The deployment is primarily managed by a GitHub Actions pipeline, triggered by a tag of the form `ast-py/v<version>`.
For example, for package version `0.4.0`, the tag should be `ast-py/v0.4.0`.

To deploy:

1. create a PR that sets the version number of the package in `__init__.py` and `docs/conf.py` to what it should be.
2. once the PR has merged, tag the merge commit (for example, `git fetch origin; git tag -m "Python AST 0.4.0" ast-py/v0.4.0 origin/main`).
3. push the tag to this repository (for example, `git push origin ast-py/v0.4.0`).

At this point, the deployment pipeline will take over and deploy the package to PyPI.
You should be able to see the progress [in the Actions tab of this repository](https://github.com/openqasm/openqasm/actions/workflows/deploy-ast.yml).
