import unittest

from antlr4 import *
from antlr4.tree.Trees import Trees
from source.grammar.qasm3Lexer import qasm3Lexer
from source.grammar.qasm3Parser import qasm3Parser

def get_pretty_tree(tree, rule_names: list = None, parser: Parser = None, level: int = 0) -> str:
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
    if parser is not None:
        rule_names = parser.ruleNames
    node_text = Trees.getNodeText(tree, rule_names)
    pretty_tree = level*" " + node_text + "\n"
    if tree.getChildCount() > 0:
        for i in range(0, tree.getChildCount()):
            pretty_tree += get_pretty_tree(tree.getChild(i), rule_names=rule_names, level=level+1)
    return pretty_tree

class TestGrammar(unittest.TestCase):

    def setup(self, text):
        self.path = "source/grammar/tests"
        lexer = qasm3Lexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        parser = qasm3Parser(stream)

        tree = parser.program()
        pretty_tree = get_pretty_tree(tree, None, parser)
        return pretty_tree

    def test_addition(self):
        tree = self.setup("2+2;")
        with open(self.path+"/outputs/add.qasm", "r") as test_file:
            test_tree = test_file.read()

        self.assertEqual(tree, test_tree)

if __name__ == '__main__':
    unittest.main()
