import itertools
import os
import pathlib
from typing import List, Union, Sequence

import pytest
import yaml

import openqasm_reference_parser

TEST_DIR = pathlib.Path(__file__).parent
REPO_DIR = TEST_DIR.parents[2]


def find_files(
    directory: Union[str, os.PathLike], suffix: str = "", raw: bool = False
) -> List:
    """Recursively find all files in ``directory`` that end in ``suffix``.

    Args:
        directory: the (absolute) directory to search for the files.
        suffix: the string that filenames should end in to be returned.  Files
            without this suffix are ignored.  This is useful for limiting files
            to those with a particular extension.
        raw: If false (the default), the output elements are all
        ``pytest.param`` instances with nice ids.  If true, then only the file
        names are returned, without the wrapping parameter.

    Returns:
        By default, a list of ``pytest`` parameters, where the value is a string
        of the absolute path to a file, and the id is a string of the path
        relative to the given directory.  If ``raw`` is given, then just a list
        of the files as ``pathlib.Path`` instances.
    """
    directory = pathlib.Path(directory).absolute()

    if raw:

        def output_format(root, file):
            return str(pathlib.Path(root) / file)

    else:

        def output_format(root, file):
            path = pathlib.Path(root) / file
            return pytest.param(str(path), id=str(path.relative_to(directory)))

    return [
        output_format(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(suffix)
    ]


def cases_from_lines(
    files: Union[str, os.PathLike, Sequence[Union[str, os.PathLike]]],
    skip_comments: bool = True,
    root: Union[str, os.PathLike] = TEST_DIR,
):
    """Parametrize test cases from the lines of a series of files.

    Whitespace at the start and end of the lines is stripped from the case.

    Args:
        files: The name of a file or files to draw the test cases from.  Can be
            the output of :obj:`~find_files` with ``raw=True`` to do discovery.
        skip_comments: Whether to skip lines which begin with the line-comment
            sequence "//".
        root: The directory to quote the filenames relative to, when generating
            the test id.

    Returns:
        A sequence of pytest parameters with the individual test cases and their
        ids.  The id is formed of the file name and the line number the case was
        taken from.
    """
    if isinstance(files, (str, os.PathLike)):
        files = (files,)
    root = pathlib.Path(root)

    def output_format(line, filename, line_number):
        relative_filename = pathlib.Path(filename).relative_to(root)
        return pytest.param(
            line,
            id=f"{relative_filename}:{line_number + 1}",
        )

    out = []
    for filename in files:
        with open(filename, "r") as file:
            for line_number, line in enumerate(file):
                line = line.strip()
                if not line or (skip_comments and line.startswith("//")):
                    continue
                out.append(output_format(line, filename, line_number))
    return out


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
    @pytest.mark.parametrize(
        "statement",
        cases_from_lines(
            find_files(TEST_DIR / "invalid" / "statements", ".qasm", raw=True),
            root=TEST_DIR / "invalid" / "statements",
        ),
    )
    def test_single_global_statement(self, statement):
        with pytest.raises(openqasm_reference_parser.Qasm3ParserError):
            openqasm_reference_parser.pretty_tree(program=statement)

    @pytest.mark.parametrize(
        "statement",
        cases_from_lines(
            TEST_DIR / "valid" / "statements" / "globals.qasm",
            root=TEST_DIR / "valid" / "statements",
        )
    )
    def test_scoped_global_statements(self, statement):
        # Check that the statement is a valid global statement ...
        openqasm_reference_parser.pretty_tree(program=statement)
        # ... but it fails if not in the global scope.
        scoped = f"if (true) {{ {statement} }}"
        with pytest.raises(openqasm_reference_parser.Qasm3ParserError):
            openqasm_reference_parser.pretty_tree(program=scoped)
