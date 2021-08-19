import itertools
import os
import pathlib
from typing import List, Union

import pytest
import yaml

import openqasm_reference_parser

TEST_DIR = pathlib.Path(__file__).parent
REPO_DIR = TEST_DIR.parents[2]


def find_files(directory: Union[str, os.PathLike], suffix: str = "") -> List:
    """Recursively find all files in ``directory`` that end in ``suffix``.

    Returns:
        A list of ``pytest`` parameters, where the value is a string of the
        absolute path to a file, and the id is a string of the path relative to
        the given directory.
    """
    directory = pathlib.Path(directory).absolute()

    def parameter(root, file):
        path = pathlib.Path(root) / file
        return pytest.param(str(path), id=str(path.relative_to(directory)))

    return [
        parameter(root, file)
        for root, _, files in os.walk(directory) for file in files
        if file.endswith(suffix)
    ]


@pytest.mark.parametrize(
    "filename",
    find_files(TEST_DIR / "reference", suffix=".yaml"),
)
def test_reference_output(filename):
    """Test that the reference files parse to the exact expected output."""
    with open(filename, "r") as file:
        obj = yaml.load(file, Loader=yaml.FullLoader)
    # Make sure the YAML files have only the correct keys.
    assert set(obj) == {"reference", "source"}
    parsed = openqasm_reference_parser.pretty_tree(program=obj["source"])
    assert parsed == obj["reference"]


@pytest.mark.parametrize(
    "filename",
    find_files(REPO_DIR / "examples", suffix=".qasm"),
)
def test_examples_parse(filename):
    """Test that the example QASM3 files all parse without error."""
    openqasm_reference_parser.pretty_tree(file=filename)


class TestInvalidProgramsFailToParse:
    valid_globals = [
        "OPENQASM 3;",
        "include 'stdgates.inc';",
        "input int[8] myvar;",
        "output int[8] myvar;",
        "def myfunc() -> int[8] { return 12; }",
        "extern myfunc () -> int[8];",
        "gate ccy a, b, c { ctrl @ ctrl @ y a, b, c; }",
        'defcalgrammar "openpulse";',
        "defcal x $0 { }",
    ]

    invalid_headers = [
        "OPENQASM int;",
        "OPENQASM 'hello, world';",
        "OPENQASM 3 3;",
        "OPENQASM 3.x;",
        "include 3;",
        "include include;",
        "include def;",
        'include "hello;',
    ]
    invalid_calibration = [
        'defcalgrammar "openpulse" defcalgrammar "openpulse";',
        'defcalgrammar 3;',
        "defcal x $0 -> int[8] -> int[8] {}",
    ]
    invalid_tokens = [
        "#;",
        "3x;",
        "x@x;",
        "3.4.3;",
        "3.4e3e3;",
    ]
    invalid_declarations = [
        # Not specifying the variable.
        "float;",
        "uint[8];",
        "fixed[7, 1];",
        "qreg[4];",
        "creg[4];",
        "complex[float[32]];",
        # Incorrect designators.
        "int myvar;",
        "int[8, 8] myvar;",
        "uint myvar;",
        "uint[8, 8] myvar;",
        "float myvar;",
        "float[8, 8] myvar;",
        "fixed myvar;",
        "fixed[8] myvar;",
        "angle myvar;",
        "angle[8, 8] myvar;",
        "bool[4] myvar;",
        "bool[4, 4] myvar;",
        "bit[4, 4] myvar;",
        "creg[2] myvar;",
        "creg[2, 2] myvar;",
        "qreg[2] myvar;",
        "qreg[2, 2] myvar;",
        "complex myvar;",
        "complex[float] myvar;",
        "complex[32] myvar;",
        "complex[mytype] myvar;",
        "complex[float[32], float[32]] myvar;",
        "complex[qreg] myvar;",
        "complex[creg] myvar;",
        "complex[qreg[8]] myvar;",
        "complex[creg[8]] myvar;",
        # Invalid identifiers.
        "int[8] int;",
        "int[8] def;",
        "int[8] 0;",
        "int[8] input;",
        # Bad assignments.
        "int[8] myvar = end;",
        "int[8] myvar =;",
        "float[32] myvar_f = int[32] myvar_i = 2;",
        # Incorrect orders.
        "myvar: int[8];",
        "myvar int[8];",
        "int myvar[8];",
        "uint myvar[8];",
        "float myvar[32];",
        "fixed myvar[7, 1];",
        # Compound assignments.
        "int[8] myvar1, myvar2;",
        "int[8] myvari, float[32] myvarf;",
        "int[8] myvari float[32] myvarf;",
    ]
    invalid_io = [
        "input int[8];",
        "output int[8];",
        "input qreg myvar[4];",
        "output qreg myvar[4];",
        "input int[8] myvar = 32;",
        "output int[8] myvar = 32;",
        "input myvar;",
        "output myvar;",
    ]
    invalid_const = [
        pytest.param("const myvar;", marks=pytest.mark.xfail),
        "const myvar = ;",
        "const int[8] myvar = 8;",
        "input const myvar = 8;",
        "output const myvar = 8;",
        "const input myvar = 8;",
        "const output myvar = 8;",
    ]
    invalid_branch = [
        "if true x $0;",
        "if false { x $0; }",
        "if (myvar += 1) { x $0; }",
        "if (int[8] myvar = 1) { x $0; }",
        "if (true);"
        "if (true) else x $0;"
        "if (true) else (false) x $0;"
        "if (reset $0) { x $1; }",
    ]
    invalid_loop = [
        "for myvar in { 1, 2, 3 };",
        "for myvar1, myvar2 in { 1, 2, 3 } { x $0; }",
        "for myvar in { x $0; } { x $0; }",
        "for myvar in for { x $0; }",
        "for myvar { x $0; }",
        "for (true) { x $0; }",
        "for { x $0; }",
        "for for in { 1, 2, 3 } { x $0; }",
        "for in { 1, 2, 3 } { x $0; }",
        "while true { x $0; }",
        "while (true) (true) { x $0; }",
        "while x in { 1, 2, 3 } { x $0; }",
        "while (true);",
    ]
    invalid_gate_applications = [
        "U () $0;",
        "U (1)(2) $0;",
        "notmodifier @ x $0;",
        "pow @ x $0;",
        "pow(2, 3) @ x $0;",
        "ctrl(2, 3) @ x $0, $1;",
        "negctrl(2, 3) @ x $0, $1;",
        "inv(1) @ ctrl @ x $0, $1;",
        # Global phase is defined in the grammar to be the last modifier.
        "gphase(pi) @ ctrl @ x $0, $1;",
    ]

    @pytest.mark.parametrize(
        "statement",
        list(itertools.chain(
            invalid_headers,
            invalid_calibration,
            invalid_tokens,
            invalid_io,
            invalid_declarations,
            invalid_const,
            invalid_branch,
            invalid_loop,
            invalid_gate_applications,
        )),
    )
    def test_single_global_statement(self, statement):
        with pytest.raises(openqasm_reference_parser.Qasm3ParserError):
            openqasm_reference_parser.pretty_tree(program=statement)

    @pytest.mark.parametrize("statement", valid_globals)
    def test_scoped_global_statements(self, statement):
        # Check that the statement is a valid global statement ...
        openqasm_reference_parser.pretty_tree(program=statement)
        # ... but it fails if not in the global scope.
        scoped = f"if (true) {{ {statement} }}"
        with pytest.raises(openqasm_reference_parser.Qasm3ParserError):
            openqasm_reference_parser.pretty_tree(program=scoped)
