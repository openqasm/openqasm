from . import ast

__all__ = ["precedence"]

_PRECEDENCE_TABLE = {
    ast.Concatenation: 0,
    # ... the rest of the binary operations come very early ...
    ast.UnaryExpression: 11,
    # ... power expression ...
    # "Call"-like expressions bind very tightly.
    ast.IndexExpression: 13,
    ast.FunctionCall: 13,
    ast.Cast: 13,
    ast.DurationOf: 13,
    # Identifiers/literals are the top, since you never need to put brackets
    # around a single literal or identifier.
    ast.Identifier: 14,
    ast.BitstringLiteral: 14,
    ast.BooleanLiteral: 14,
    ast.DurationLiteral: 14,
    ast.FloatLiteral: 14,
    ast.ImaginaryLiteral: 14,
    ast.IntegerLiteral: 14,
    ast.ArrayLiteral: 14,
}

_BINARY_PRECEDENCE_TABLE = {
    ast.BinaryOperator["||"]: 1,
    ast.BinaryOperator["&&"]: 2,
    ast.BinaryOperator["|"]: 3,
    ast.BinaryOperator["^"]: 4,
    ast.BinaryOperator["&"]: 5,
    # equality
    ast.BinaryOperator["=="]: 6,
    ast.BinaryOperator["!="]: 6,
    # comparsions
    ast.BinaryOperator["<"]: 7,
    ast.BinaryOperator["<="]: 7,
    ast.BinaryOperator[">"]: 7,
    ast.BinaryOperator[">="]: 7,
    # bitshifts
    ast.BinaryOperator["<<"]: 8,
    ast.BinaryOperator[">>"]: 8,
    # additive
    ast.BinaryOperator["+"]: 9,
    ast.BinaryOperator["-"]: 9,
    # multiplicative
    ast.BinaryOperator["*"]: 10,
    ast.BinaryOperator["/"]: 10,
    ast.BinaryOperator["%"]: 10,
    # ... unary expression goes here ...
    ast.BinaryOperator["**"]: 12,
}


def precedence(node: ast.QASMNode) -> int:
    """Get the integer value of the precedence level of an expression node.

    The actual numeric value has no real meaning and is subject to change
    between different versions of the AST and versions of the language.  It is
    only intended to be used as a key for comparisons between different
    expressions.

    The number is such that if an AST node representing expression ``A``
    contains a subexpression ``B``, then on output, ``B`` needs brackets around
    it if its precedence is lower than ``A``.  If ``A`` is a left-associative
    (right-associative) binary operator, then its right-hand (left-hand)
    subexpression also needs brackets if the precendence of the two are equal.
    """
    if node.__class__ in _PRECEDENCE_TABLE:
        return _PRECEDENCE_TABLE[node.__class__]
    if isinstance(node, ast.BinaryExpression):
        return _BINARY_PRECEDENCE_TABLE[node.op]
    raise ValueError(f"Node '{node}' has no expression precedence. Is it an Expression?")
