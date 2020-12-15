import sys
from antlr4 import *
from qasm3Lexer import qasm3Lexer
from qasm3Parser import qasm3Parser
from qasm3Listener import qasm3Listener

from antlr4.tree.Trees import Trees
import re

def pprint_lisp_tree(lisp_tree):
    indent = 0
    ltree = lisp_tree[1:len(lisp_tree)-1]
    ltree = ltree.replace('(', ' ( ')
    ltree = ltree.replace(')', ' ) ')
    ltree = ltree.split(' ')
    print("program")
    for token in ltree:
        print(' '*indent, end='')
        if token == '(':
            indent += 1
            print()
        elif token == ')':

    import pdb; pdb.set_trace()

    """
    for i, char in enumerate(lisp_tree):
        if char == '(':
            if i != 0:  # skip first (
                indent += 1
                print('\n'+' '*indent, end='')
        elif char == ')':
            if i != len(lisp_tree) - 1:  # skip last )
                indent -= 1
        else:
            print(char, end='')
    """

def main(argv):
    input = FileStream(argv[1])
    lexer = qasm3Lexer(input)
    stream = CommonTokenStream(lexer)
    parser = qasm3Parser(stream)
    tree = parser.program()
    lisp_tree = Trees.toStringTree(tree, None, parser)
    import pdb; pdb.set_trace()
    pprint_lisp_tree(lisp_tree)
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main(sys.argv)
