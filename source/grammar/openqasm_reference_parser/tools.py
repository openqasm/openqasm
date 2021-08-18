import contextlib
import io

import antlr4
from antlr4.tree.Trees import Trees, ParseTree

from . import Qasm3ParserError
from .qasm3Lexer import qasm3Lexer
from .qasm3Parser import qasm3Parser

__all__ = ["pretty_tree"]


def pretty_tree(program: str = None, file: str = None) -> str:
    if program is not None and file is not None:
        raise ValueError("Must supply only one of 'program' and 'file'.")
    if program is not None:
        input_stream = antlr4.InputStream(program)
    elif file is not None:
        input_stream = antlr4.FileStream(file, encoding="utf-8")
    else:
        raise TypeError("One of 'program' and 'file' must be supplied.")

    # ANTLR errors (lexing and parsing) are sent to stderr, which we redirect
    # to the variable `err`.
    with io.StringIO() as err, contextlib.redirect_stderr(err):
        lexer = qasm3Lexer(input_stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = qasm3Parser(token_stream)
        tree = _pretty_tree_inner(parser.program(), parser.ruleNames, 0)
        error = err.getvalue()
    if error:
        raise Qasm3ParserError("Parse tree build failed. Error:\n" + error)
    return tree


def _pretty_tree_inner(parse_tree: ParseTree, rule_names: list, level: int) -> str:
    indent = "  " * level
    tree = indent + Trees.getNodeText(parse_tree, rule_names) + "\n"
    return tree + "".join(
        _pretty_tree_inner(parse_tree.getChild(i), rule_names, level + 1)
        for i in range(parse_tree.getChildCount())
    )
