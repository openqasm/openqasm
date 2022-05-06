"""
=============================
Parser (``openpulse.parser``)
=============================

Tools for parsing OpenPulse programs into the :obj:`reference AST <openpulse.ast>`.

The quick-start interface is simply to call ``openpulse.parse``:

.. currentmodule:: openpulse
.. autofunction:: openpulse.parse

The rest of this module provides some lower-level internals of the parser.

.. currentmodule:: openpulse.parser
.. autoclass:: OpenPulseNodeVisitor
"""

# pylint: disable=wrong-import-order

__all__ = [
    "parse",
    "OpenPulseNodeVisitor",
]

import re

try:
    from antlr4 import CommonTokenStream, InputStream
    from antlr4.tree.Tree import TerminalNode
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from openqasm3.parser import get_span, add_span, span, QASMNodeVisitor
from openqasm3.antlr.qasm3Parser import qasm3Parser

from .antlr.openpulseLexer import openpulseLexer
from .antlr.openpulseParser import openpulseParser
from .antlr.openpulseParserVisitor import openpulseParserVisitor
from .ast import (
    CalibrationDefinition,
    ClassicalDeclaration,
    ExternDeclaration,
    Identifier,
    Program,
    PulseType,
    PulseTypeName,
    CalibrationBlock,
)


def parse(input_: str) -> Program:
    """
    Parse a complete OpenPulse program from a string.

    :param input_: A string containing a complete OpenQASM 3 program.
    :return: A complete :obj:`~ast.Program` node.
    """
    lexer = openpulseLexer(InputStream(input_))
    stream = CommonTokenStream(lexer)
    parser = openpulseParser(stream)

    tree = parser.program()

    return OpenPulseNodeVisitor().visitProgram(tree)


# Hacks to reuse visitor methods in OpenPulseNodeVisitor
# QASMNodeVisitor use isinstance check on a few Context types so we have to use the hack below
openpulseParser.ArrayInitializerContext = type(
    "ArrayInitializerContext", (qasm3Parser.ArrayInitializerContext,), {}
)
openpulseParser.RangeDefinitionContext = type(
    "RangeDefinitionContext", (qasm3Parser.RangeDefinitionContext,), {}
)
openpulseParser.ExpressionContext = type("ExpressionContext", (qasm3Parser.ExpressionContext,), {})


class OpenPulseNodeVisitor(openpulseParserVisitor):
    """Base class for the visitor of the OpenPulse AST."""
    @span
    def visitCalibrationDefinition(self, ctx: openpulseParser.CalibrationDefinitionContext):
        # We overide this method in QASMNodeVisitor.visitCalibrationDefinition as we have a
        # concrete pulse grammar.
        body_chars = []  # Python concatenation is slow so we build a list first
        for i in range(ctx.getChildCount() - 2, 0, -1):
            node = ctx.getChild(i)
            if isinstance(node, TerminalNode):
                body_chars.insert(0, node.getText())
            else:
                break

        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))

        statements = [self.visit(statement) for statement in ctx.calStatement()]
        if ctx.returnStatement():
            statements.append(self.visit(ctx.returnStatement()))

        return CalibrationDefinition(
            name=name,
            arguments=self.visit(ctx.calibrationArgumentList().getChild(0))
            if ctx.calibrationArgumentList()
            else [],
            qubits=[
                add_span(Identifier(id.getText()), get_span(id))
                for id in ctx.identifierList().Identifier()
            ],
            return_type=self.visit(ctx.returnSignature().classicalType())
            if ctx.returnSignature()
            else None,
            body=statements,
        )

    # Pulse parser
    @span
    def visitPulseDeclaration(self, ctx: openpulseParser.PulseDeclarationContext):
        return ClassicalDeclaration(
            type=self.visit(ctx.pulseType()),
            identifier=add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            init_expression=self.visit(ctx.equalsExpression().expression())
            if ctx.equalsExpression()
            else None,
        )

    @span
    def visitPulseType(self, ctx: openpulseParser.PulseTypeContext):
        return PulseType(type=PulseTypeName[ctx.getText()])

    @span
    def visitCalExternDeclaration(self, ctx: openpulseParser.CalExternDeclarationContext):
        classical_types = (
            [self.visit(cal_type) for cal_type in ctx.calTypeList().calType()]
            if ctx.calTypeList()
            else []
        )

        return ExternDeclaration(
            name=ctx.Identifier().getText(),
            classical_types=classical_types,
            return_type=self.visit(ctx.calType()) if ctx.calType() else None,
        )

    @span
    def visitCalType(self, ctx: openpulseParser.CalTypeContext):
        if ctx.classicalType():
            return self.visit(ctx.classicalType())
        elif ctx.pulseType():
            return self.visit(ctx.pulseType())

    @span
    def visitCalBlock(self, ctx: openpulseParser.CalBlockContext):
        return CalibrationBlock(body=[self.visit(statement) for statement in ctx.calStatement()])


# Try to reuse some methods from QASMNodeVisitor
p = re.compile("_?visit.+")
excluded = ["visitErrorNode", "visitCalibrationDefinition", "visitChildren", "visitTerminal"]
for m in QASMNodeVisitor.__dict__:
    if p.match(m) and not m in excluded:
        setattr(OpenPulseNodeVisitor, m, getattr(QASMNodeVisitor, m))
