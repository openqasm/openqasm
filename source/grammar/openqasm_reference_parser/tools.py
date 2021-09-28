import contextlib
import io

import antlr4
from antlr4.tree.Trees import Trees, ParseTree

from . import Qasm3ParserError
from .qasm3Lexer import qasm3Lexer
from .qasm3Parser import qasm3Parser

__all__ = ["pretty_tree"]


def pretty_tree(*, program: str = None, file: str = None) -> str:
    """Get a pretty-printed string of the parsed AST of the QASM input.

    The input will be taken either verbatim from the string ``program``, or read
    from the file with name ``file``.  Use exactly one of the possible input
    arguments, passed by keyword.

    Args:
        program: a string containing the QASM to be parsed.
        file: a string of the filename containing the QASM to be parsed.

    Returns:
        a pretty-printed version of the parsed AST of the given program.

    Raises:
        ValueError: no input is given, or too many inputs are given.
        Qasm3ParserError: the input was not parseable as valid QASM 3.
    """
    if program is not None and file is not None:
        raise ValueError("Must supply only one of 'program' and 'file'.")
    if program is not None:
        input_stream = antlr4.InputStream(program)
    elif file is not None:
        input_stream = antlr4.FileStream(file, encoding="utf-8")
    else:
        raise ValueError("One of 'program' and 'file' must be supplied.")

    # ANTLR errors (lexing and parsing) are sent to stderr, which we redirect
    # to the variable `err`.
    with io.StringIO() as err, contextlib.redirect_stderr(err):
        lexer = qasm3Lexer(input_stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = qasm3Parser(token_stream)
        tree = _pretty_tree_inner(parser.program(), parser.ruleNames, 0)
        error = err.getvalue()
    if error:
        raise Qasm3ParserError(f"Parse tree build failed. Error:\n{error}")
    return tree


def _pretty_tree_inner(parse_tree: ParseTree, rule_names: list, level: int) -> str:
    """Internal recursive routine used in pretty-printing the parse tree.

    Args:
        parse_tree: a node in the parse tree of the output of the ANTLR parser.
        rule_names: the ANTLR-generated list of rule names in the grammar.
        level: the current indentation level.

    Returns:
        the pretty-printed tree starting from this node, indented correctly.
    """
    indent = "  " * level
    tree = indent + Trees.getNodeText(parse_tree, rule_names) + "\n"
    return tree + "".join(
        _pretty_tree_inner(parse_tree.getChild(i), rule_names, level + 1)
        for i in range(parse_tree.getChildCount())
    )
