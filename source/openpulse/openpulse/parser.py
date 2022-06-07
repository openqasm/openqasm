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

from contextlib import contextmanager
import re
from typing import List

try:
    from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from openqasm3.parser import (
    get_span,
    add_span,
    span,
    QASMNodeVisitor,
    _visit_identifier,
    _raise_from_context,
)
from openqasm3.antlr.qasm3Parser import qasm3Parser

from .antlr.openpulseLexer import openpulseLexer
from .antlr.openpulseParser import openpulseParser
from .antlr.openpulseParserVisitor import openpulseParserVisitor
from . import ast


def parse(input_: str) -> ast.Program:
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


class OpenPulseNodeVisitor(openpulseParserVisitor):
    """Base class for the visitor of the OpenPulse AST."""

    def __init__(self):
        # A stack of "contexts", each of which is a stack of "scopes".  Contexts
        # are for the main program, gates and subroutines, while scopes are
        # loops, if/else and manual scoping constructs.  Each "context" always
        # contains at least one scope: the base ``ParserRuleContext`` that
        # opened it.
        self._contexts: List[List[ParserRuleContext]] = []

    @contextmanager
    def _push_context(self, ctx: ParserRuleContext):
        self._contexts.append([ctx])
        yield
        self._contexts.pop()

    @contextmanager
    def _push_scope(self, ctx: ParserRuleContext):
        self._contexts[-1].append(ctx)
        yield
        self._contexts[-1].pop()

    def _current_context(self):
        return self._contexts[-1]

    def _current_scope(self):
        return self._contexts[-1][-1]

    def _current_base_scope(self):
        return self._contexts[-1][0]

    def _in_global_scope(self):
        return len(self._contexts) == 1 and len(self._contexts[0]) == 1

    def _in_gate(self):
        return isinstance(self._current_base_scope(), openpulseParser.GateStatementContext)

    def _in_subroutine(self):
        return isinstance(self._current_base_scope(), openpulseParser.DefStatementContext)

    def _in_loop(self):
        return any(
            isinstance(
                scope, (openpulseParser.ForStatementContext, openpulseParser.WhileStatementContext)
            )
            for scope in reversed(self._current_context())
        )

    def _in_defcal(self):
        return isinstance(self._current_base_scope(), openpulseParser.DefcalStatementContext)

    @span
    def _visitPulseType(self, ctx: openpulseParser.ScalarTypeContext):
        if ctx.WAVEFORM():
            return ast.WaveformType()
        if ctx.PORT():
            return ast.PortType()
        if ctx.FRAME():
            return ast.FrameType()

    @span
    def visitArrayLiteral(self, ctx: openpulseParser.ArrayLiteralContext):
        array_literal_element = (
            openpulseParser.ExpressionContext,
            openpulseParser.ArrayLiteralContext,
        )

        def predicate(child):
            return isinstance(child, array_literal_element)

        return ast.ArrayLiteral(
            values=[self.visit(element) for element in ctx.getChildren(predicate=predicate)],
        )

    def visitCalibrationGrammarStatement(
        self, ctx: openpulseParser.CalibrationGrammarStatementContext
    ):
        assert (
            ctx.StringLiteral().getText() == '"openpulse"'
        ), "Expected 'openpulse' as the calibration grammar"
        return QASMNodeVisitor.visitCalibrationGrammarStatement(self, ctx)

    @span
    def visitCalStatement(self, ctx: openpulseParser.CalStatementContext):
        return ast.CalibrationBlock(body=[self.visit(statement) for statement in ctx.statement()])

    def visitScalarType(self, ctx: openpulseParser.ScalarTypeContext):
        if ctx.WAVEFORM() or ctx.PORT() or ctx.FRAME():
            return self._visitPulseType(ctx)
        else:
            return QASMNodeVisitor.visitScalarType(self, ctx)

    @span
    def visitDefcalStatement(self, ctx: openpulseParser.DefcalStatementContext):
        # We overide this method in QASMNodeVisitor.visitCalibrationDefinition as we have a
        # concrete pulse grammar.
        with self._push_context(ctx):
            statements = [self.visit(statement) for statement in ctx.statement()]
        arguments = (
            [self.visit(argument) for argument in ctx.argumentDefinitionList().argumentDefinition()]
            if ctx.argumentDefinitionList()
            else []
        )
        qubits = (
            [
                add_span(ast.Identifier(qubit.getText()), get_span(qubit))
                for qubit in ctx.hardwareQubitList().HardwareQubit()
            ]
            if ctx.hardwareQubitList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )

        return ast.CalibrationDefinition(
            name=_visit_identifier(ctx.Identifier()),
            arguments=arguments,
            qubits=qubits,
            return_type=return_type,
            body=statements,
        )

    def visitIndexOperator(self, ctx: openpulseParser.IndexOperatorContext):
        if ctx.setExpression():
            return self.visit(ctx.setExpression())

        index_element = (
            openpulseParser.ExpressionContext,
            openpulseParser.RangeExpressionContext,
        )

        def predicate(child):
            return isinstance(child, index_element)

        return [self.visit(child) for child in ctx.getChildren(predicate=predicate)]

    @span
    def visitRangeExpression(self, ctx: openpulseParser.RangeExpressionContext):
        # start, end and step are all optional as in [:]
        # It could be [start:end] or [start:step:end]
        start = None
        end = None
        step = None
        colons_seen = 0

        for child in ctx.getChildren():
            if isinstance(child, openpulseParser.ExpressionContext):
                expression = self.visit(child)
                if colons_seen == 0:
                    start = expression
                elif colons_seen == 1:
                    end = expression
                else:
                    step = end
                    end = expression
            elif child.getText() == ":":
                colons_seen += 1

        return ast.RangeDefinition(start=start, end=end, step=step)

    @span
    def visitReturnStatement(self, ctx: qasm3Parser.ReturnStatementContext):
        if not self._in_subroutine() and not self._in_defcal():
            _raise_from_context(ctx, "'return' statement outside subroutine or defcal")
        if ctx.expression():
            expression = self.visit(ctx.expression())
        elif ctx.measureExpression():
            expression = self.visit(ctx.measureExpression())
        else:
            expression = None
        return ast.ReturnStatement(expression=expression)


# Try to reuse some methods from QASMNodeVisitor
# We exclude some methods. The first 3 are from the generated openpulseParserVisitor class.
# The rest are redefined in the OpenPulseNodeVisitor class.
# We need to redefine some methods does instanceof checks.
p = re.compile("_?(visit).+")
excluded = [
    "visitChildren",
    "visitErrorNode",
    "visitTerminal",
    "visitArrayLiteral",
    "visitCalibrationGrammarStatement",
    "visitDefcalStatement",
    "visitIndexOperator",
    "visitRangeExpression",
    "visitReturnStatement",
    "visitScalarType",
]
for m in QASMNodeVisitor.__dict__:
    if p.match(m) and not m in excluded:
        setattr(OpenPulseNodeVisitor, m, getattr(QASMNodeVisitor, m))
