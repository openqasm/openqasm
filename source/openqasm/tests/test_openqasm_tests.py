import openqasm3


def test_examples(example_file):
    """Loop through all example files, verify that the ast_parser can parse the file.

    The `example_file` fixture is generated in `conftest.py`.  These tests are automatically skipped
    if the examples directly cannot be found.
    """
    with open(example_file) as f:
        source = f.read()
        openqasm3.parse(source)
