import pathlib
import pytest

from openqasm.parser.antlr.qasm_parser import parse


TEST_DIR = pathlib.Path(__file__).parent
ROOT_DIR = TEST_DIR.parents[2]
EXAMPLES_DIR = ROOT_DIR / "examples"
EXAMPLES = tuple(EXAMPLES_DIR.glob("**/*.qasm"))


@pytest.fixture(params=EXAMPLES, ids=lambda x: str(x.relative_to(EXAMPLES_DIR)))
def example_file(request):
    return str(request.param)


def test_examples(example_file):
    """Loop through all example files, verify that the ast_parser can parse the file.

    Examples located at: ``openqasm/examples``.
    """
    with open(example_file) as f:
        source = f.read()
        parse(source)
