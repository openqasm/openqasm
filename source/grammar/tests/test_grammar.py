import unittest
import io
import os
from contextlib import redirect_stderr

import yaml

from antlr4 import *
from antlr4.tree.Trees import Trees

# add lexer, parser to Python path and import
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qasm3Lexer import qasm3Lexer
from qasm3Parser import qasm3Parser


def get_pretty_tree(
    tree: "ParseTree", rule_names: list = None, parser: Parser = None, level: int = 0
) -> str:
    """Take antlr ``ParseTree`` and return indented tree format for test comparison.

    Adapted from ``antrl4.tree.Trees.toStringTree()`` method.

    Args:
        tree: The antlr parse tree.
        rule_names: Names of parser rules.
        parser: The parser used to generated the tree.
        level: Level of tree (used for indentation).

    Returns:
        Pretty tree format (indents of one space at each level).
    """
    indent_value = "  "  # indent using two spaces to match ``yaml`` reference files

    if parser is not None:
        rule_names = parser.ruleNames

    node_text = Trees.getNodeText(tree, rule_names)
    pretty_tree = level * indent_value + node_text + "\n"

    if tree.getChildCount() > 0:
        for i in range(0, tree.getChildCount()):
            pretty_tree += get_pretty_tree(tree.getChild(i), rule_names=rule_names, level=level + 1)

    return pretty_tree


def build_parse_tree(input_str: str, using_file: bool = False) -> str:
    """Build indented parse tree in string format.

    Args:
        input_str: Input program or file path.
        using_file: Whether input string is source program or file path.

    Raises:
        Exception: If build fails (at any stage: lexing or parsing).

    Returns:
        Parse tree string in indented format.
    """
    input = FileStream(input_str, encoding='utf-8') if using_file else InputStream(input_str)
    pretty_tree = ""
    # antlr errors (lexing and parsing) sent to stdout -> redirect to variable err
    with io.StringIO() as err, redirect_stderr(err):
        lexer = qasm3Lexer(input)
        stream = CommonTokenStream(lexer)
        parser = qasm3Parser(stream)
        tree = parser.program()

        pretty_tree = get_pretty_tree(tree, None, parser)

        error = err.getvalue()
        if error:
            print(input_str)
            raise Exception("Parse tree build failed. Error:\n" + error)

    return pretty_tree

class TestGrammar(unittest.TestCase):
    """Test the ANTLR grammar w/ python unittest."""

    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))  # tests/ dir
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(test_dir)))  # project root dir
        self.examples_path = os.path.join(root_dir, "examples/")
        self.test_path = os.path.join(test_dir, "outputs")

    def load_and_compare_yaml(self, test_str):
        """Process test yaml files. Yaml is expected to contain OpenQasm3.0 source code, which is
        parsed. The resulting parse tree is compared to a reference output.

        The yaml keys are ``source`` and ``reference``, respectively.

        Args:
            test_str (str): Relative path of test yaml file, ie ``add.yaml``.
        """
        if not "yaml" in test_str:
            raise ValueError("Test file should be in YAML format.")

        test_path = os.path.join(self.test_path, test_str)
        with open(test_path) as test_file:
            test_dict = yaml.load(test_file, Loader=yaml.FullLoader)

        if sorted(list(test_dict.keys())) != ["reference", "source"]:
            raise KeyError("Reference YAML file contain only ``source`` and ``reference`` keys.")

        qasm_source = test_dict["source"]
        parse_tree = build_parse_tree(qasm_source)
        import pdb; pdb.set_trace()
        reference = test_dict["reference"]
        self.assertEqual(parse_tree, reference)

    def test_header(self):
        """Test header."""
        self.load_and_compare_yaml("header.yaml")

    def test_global_statement(self):
        """Test global statements."""
        self.load_and_compare_yaml("subroutine.yaml")
        self.load_and_compare_yaml("kernel.yaml")
        self.load_and_compare_yaml("quantum_gate.yaml")
        # TODO: Add calibration test when pulse grammar is filled in

    def test_expression(self):
        self.load_and_compare_yaml("binary_expr.yaml")
        self.load_and_compare_yaml("unary_expr.yaml")
        self.load_and_compare_yaml("built_in_call.yaml")
        self.load_and_compare_yaml("sub_and_kern_call.yaml")

    def test_empty_gate(self):
        self.load_and_compare_yaml("empty_gate.yaml")

    def test_examples(self):
        """Loop through all example files, parse and verify that no errors are raised.

        Examples located at: ``openqasm/examples``.
        """
        examples = os.listdir(self.examples_path)
        for e in examples:
            if e != "pong.qasm":
                example_file = os.path.join(self.examples_path, e)
                if os.path.isfile(example_file):
                    tree = build_parse_tree(example_file, using_file=True)


if __name__ == "__main__":
    unittest.main()
