import pytest
from openqasm3 import parse_version

LINE_ENDINGS = ["", "\n", "  ", "// comment\n", "\t", "/* OPENQASM 1.0 */", "/* \n\n */"]


@pytest.mark.parametrize("prefix", LINE_ENDINGS)
@pytest.mark.parametrize("infix", LINE_ENDINGS)
def test_ignore_spaces(prefix, infix):
    prog = f"{prefix}OPENQASM{infix}3.0;"
    assert parse_version(prog) == (3, 0)


@pytest.mark.parametrize(
    ["version_str", "version_parts"],
    [
        ("3", (3,)),
        ("3.0", (3, 0)),
        ("2", (2,)),
        ("2.0", (2, 0)),
        ("3.1", (3, 1)),
        ("3.2.3.5", (3, 2, 3, 5)),
    ],
)
def test_versions(version_str, version_parts):
    prog = f"OPENQASM {version_str};"
    assert parse_version(prog) == version_parts


def test_no_version_valid_program():
    prog = """
        include "stdgates.inc";
        qubit[2] q;
        cx q[0], q[1];
    """
    assert parse_version(prog) is None


def test_ignore_non_syntactic_version():
    # The version number has to be the first non-comment line.
    prog = """
        include "stdgates.inc";
        OPENQASM 3.0;
    """
    assert parse_version(prog) is None
