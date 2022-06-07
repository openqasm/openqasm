# Copied from openqasm3. OpenPulse parser should be able to parse openqasm3 examples
import openpulse


def test_examples(example_file):
    """Loop through all example files, verify that the ast_parser can parse the file.

    The `example_file` fixture is generated in `conftest.py`.  These tests are automatically skipped
    if the examples directly cannot be found.
    """
    with open(example_file) as f:
        source = f.read()
        openpulse.parse(source)
