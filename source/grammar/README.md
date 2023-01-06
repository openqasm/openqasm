# OpenQASM 3.0 Grammar Reference

The reference grammar is written in [ANTLR](https://www.antlr.org/).
The lexer rules are in the file [qasm3Lexer.g4](./qasm3Lexer.g4), and
the parser rules are in the file [qasm3Parser.g4](./qasm3Parser.g4).

This directory also contains a very basic Python parser, which is simply built from the reference grammar and used to test against the examples.


## Requisites

Building the grammar only requires ANTLR 4.
You can likely get a copy of ANTLR using your system package manager if you are on Unix, or from `brew` if you are on macOS.
You could also follow [these instructions](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).

Running the Python version of the parser also requires the ANTLR Python runtime.
You can install this with `pip` by
```bash
pip install antlr4-python3-runtime==<version>
```
where `<version>` should exactly match the version of ANTLR 4 you installed.
If you let `pip` do this automatically when it installs the reference parser, it will likely pull the wrong version, and produce errors during use.


## Building the Python Parser

1. Build the grammar files into the package directory with
    ```bash
    <antlr command> -o openqasm_reference_parser -Dlanguage=Python3 -visitor qasm3Lexer.g4 qasm3Parser.g4
    ```
   `<antlr command>` should be replaced with however you invoke ANTLR on your system.
   If you used a package manager, it is likely `antlr4` or `antlr`.
   If you followed the "Getting Started" instructions, it is likely just the `antlr4` alias, or it might be `java -jar <path/to/antlr.jar>`.
2. Install the Python package with `pip install -e .`.


## Run the Tests

1. Make sure the Python parser is built and available on the Python path.
2. Install the testing requirements with `pip install -e .[tests]` or `pip install -r requirements-dev.txt`.
3. Run `pytest`.
