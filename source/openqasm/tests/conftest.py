import collections
import pathlib

import pytest

import openqasm3

TEST_DIR = pathlib.Path(__file__).parent
ROOT_DIR = TEST_DIR.parents[2]
EXAMPLES_DIR = ROOT_DIR / "examples"
EXAMPLES = tuple(EXAMPLES_DIR.glob("**/*.qasm"))


# Session scoped because we want the parsed examples to be session scoped as well.
@pytest.fixture(params=EXAMPLES, ids=lambda x: str(x.relative_to(EXAMPLES_DIR)), scope="session")
def example_file(request):
    return str(request.param)


_ExampleASTReturn = collections.namedtuple("_ExampleASTReturn", ("filename", "ast"))


# Session scoped to avoid paying the parsing cost of each file multiple times (ANTLR-based parsing
# isn't the speediest).
@pytest.fixture(scope="session")
def parsed_example(example_file):
    """The parsed AST of each of the example OpenQASM files, and its filename.  The two attributes
    are `filename` and `ast`."""
    with open(example_file, "r") as f:
        content = f.read()
    return _ExampleASTReturn(example_file, openqasm3.parse(content))
