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

    def fmt(root, file):
        path = pathlib.Path(root) / file
        return pytest.param(str(path), id=str(path.relative_to(directory)))

    return [
        fmt(root, file)
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
