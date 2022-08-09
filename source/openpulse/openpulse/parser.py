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
from typing import List

try:
    from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from openqasm3.parser import (
    span,
    QASMNodeVisitor,
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
        return ast.CalibrationStatement(
            body=[self.visit(statement) for statement in ctx.statement()]
        )

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
            [
                self.visit(argument)
                for argument in ctx.defcalArgumentDefinitionList().defcalArgumentDefinition()
            ]
            if ctx.defcalArgumentDefinitionList()
            else []
        )
        qubits = [self.visit(operand) for operand in ctx.defcalOperandList().defcalOperand() or []]
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )

        return ast.CalibrationDefinition(
            name=self.visit(ctx.defcalTarget()),
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


# Reuse some QASMNodeVisitor methods in OpenPulseNodeVisitor
# The following methods are overridden in OpenPulseNodeVisitor and thuys not imported:
"""
    "visitChildren",
    "visitErrorNode",
    "visitTerminal",
    "visitArrayLiteral",
    "visitCalibrationGrammarStatement",
    "visitCalStatement",
    "visitDefcalStatement",
    "visitIndexOperator",
    "visitRangeExpression",
    "visitReturnStatement",
    "visitScalarType",
"""
OpenPulseNodeVisitor._visit_binary_expression = QASMNodeVisitor._visit_binary_expression
OpenPulseNodeVisitor.visitAdditiveExpression = QASMNodeVisitor.visitAdditiveExpression
OpenPulseNodeVisitor.visitAliasDeclarationStatement = QASMNodeVisitor.visitAliasDeclarationStatement
OpenPulseNodeVisitor.visitAliasExpression = QASMNodeVisitor.visitAliasExpression
OpenPulseNodeVisitor.visitAnnotation = QASMNodeVisitor.visitAnnotation
OpenPulseNodeVisitor.visitArgumentDefinition = QASMNodeVisitor.visitArgumentDefinition
OpenPulseNodeVisitor.visitArrayType = QASMNodeVisitor.visitArrayType
OpenPulseNodeVisitor.visitAssignmentStatement = QASMNodeVisitor.visitAssignmentStatement
OpenPulseNodeVisitor.visitBarrierStatement = QASMNodeVisitor.visitBarrierStatement
OpenPulseNodeVisitor.visitBitshiftExpression = QASMNodeVisitor.visitBitshiftExpression
OpenPulseNodeVisitor.visitBitwiseAndExpression = QASMNodeVisitor.visitBitwiseAndExpression
OpenPulseNodeVisitor.visitBitwiseOrExpression = QASMNodeVisitor.visitBitwiseOrExpression
OpenPulseNodeVisitor.visitBitwiseXorExpression = QASMNodeVisitor.visitBitwiseXorExpression
OpenPulseNodeVisitor.visitBoxStatement = QASMNodeVisitor.visitBoxStatement
OpenPulseNodeVisitor.visitBreakStatement = QASMNodeVisitor.visitBreakStatement
OpenPulseNodeVisitor.visitCallExpression = QASMNodeVisitor.visitCallExpression
OpenPulseNodeVisitor.visitCastExpression = QASMNodeVisitor.visitCastExpression
OpenPulseNodeVisitor.visitClassicalDeclarationStatement = (
    QASMNodeVisitor.visitClassicalDeclarationStatement
)
OpenPulseNodeVisitor.visitComparisonExpression = QASMNodeVisitor.visitComparisonExpression
OpenPulseNodeVisitor.visitConstDeclarationStatement = QASMNodeVisitor.visitConstDeclarationStatement
OpenPulseNodeVisitor.visitContinueStatement = QASMNodeVisitor.visitContinueStatement
OpenPulseNodeVisitor.visitDeclarationExpression = QASMNodeVisitor.visitDeclarationExpression
OpenPulseNodeVisitor.visitDefStatement = QASMNodeVisitor.visitDefStatement
OpenPulseNodeVisitor.visitDefcalArgumentDefinition = QASMNodeVisitor.visitDefcalArgumentDefinition
OpenPulseNodeVisitor.visitDefcalOperand = QASMNodeVisitor.visitDefcalOperand
OpenPulseNodeVisitor.visitDefcalTarget = QASMNodeVisitor.visitDefcalTarget
OpenPulseNodeVisitor.visitDelayStatement = QASMNodeVisitor.visitDelayStatement
OpenPulseNodeVisitor.visitDesignator = QASMNodeVisitor.visitDesignator
OpenPulseNodeVisitor.visitDurationofExpression = QASMNodeVisitor.visitDurationofExpression
OpenPulseNodeVisitor.visitEndStatement = QASMNodeVisitor.visitEndStatement
OpenPulseNodeVisitor.visitEqualityExpression = QASMNodeVisitor.visitEqualityExpression
OpenPulseNodeVisitor.visitExpressionStatement = QASMNodeVisitor.visitExpressionStatement
OpenPulseNodeVisitor.visitExternArgument = QASMNodeVisitor.visitExternArgument
OpenPulseNodeVisitor.visitExternStatement = QASMNodeVisitor.visitExternStatement
OpenPulseNodeVisitor.visitForStatement = QASMNodeVisitor.visitForStatement
OpenPulseNodeVisitor.visitGateCallStatement = QASMNodeVisitor.visitGateCallStatement
OpenPulseNodeVisitor.visitGateModifier = QASMNodeVisitor.visitGateModifier
OpenPulseNodeVisitor.visitGateOperand = QASMNodeVisitor.visitGateOperand
OpenPulseNodeVisitor.visitGateStatement = QASMNodeVisitor.visitGateStatement
OpenPulseNodeVisitor.visitIfStatement = QASMNodeVisitor.visitIfStatement
OpenPulseNodeVisitor.visitIncludeStatement = QASMNodeVisitor.visitIncludeStatement
OpenPulseNodeVisitor.visitIndexExpression = QASMNodeVisitor.visitIndexExpression
OpenPulseNodeVisitor.visitIndexedIdentifier = QASMNodeVisitor.visitIndexedIdentifier
OpenPulseNodeVisitor.visitIoDeclarationStatement = QASMNodeVisitor.visitIoDeclarationStatement
OpenPulseNodeVisitor.visitLiteralExpression = QASMNodeVisitor.visitLiteralExpression
OpenPulseNodeVisitor.visitLogicalAndExpression = QASMNodeVisitor.visitLogicalAndExpression
OpenPulseNodeVisitor.visitLogicalOrExpression = QASMNodeVisitor.visitLogicalOrExpression
OpenPulseNodeVisitor.visitMeasureArrowAssignmentStatement = (
    QASMNodeVisitor.visitMeasureArrowAssignmentStatement
)
OpenPulseNodeVisitor.visitMeasureExpression = QASMNodeVisitor.visitMeasureExpression
OpenPulseNodeVisitor.visitMultiplicativeExpression = QASMNodeVisitor.visitMultiplicativeExpression
OpenPulseNodeVisitor.visitOldStyleDeclarationStatement = (
    QASMNodeVisitor.visitOldStyleDeclarationStatement
)
OpenPulseNodeVisitor.visitParenthesisExpression = QASMNodeVisitor.visitParenthesisExpression
OpenPulseNodeVisitor.visitPowerExpression = QASMNodeVisitor.visitPowerExpression
OpenPulseNodeVisitor.visitPragma = QASMNodeVisitor.visitPragma
OpenPulseNodeVisitor.visitProgram = QASMNodeVisitor.visitProgram
OpenPulseNodeVisitor.visitQuantumDeclarationStatement = (
    QASMNodeVisitor.visitQuantumDeclarationStatement
)
OpenPulseNodeVisitor.visitResetStatement = QASMNodeVisitor.visitResetStatement
OpenPulseNodeVisitor.visitScope = QASMNodeVisitor.visitScope
OpenPulseNodeVisitor.visitSetExpression = QASMNodeVisitor.visitSetExpression
OpenPulseNodeVisitor.visitStatement = QASMNodeVisitor.visitStatement
OpenPulseNodeVisitor.visitStatementOrScope = QASMNodeVisitor.visitStatementOrScope
OpenPulseNodeVisitor.visitUnaryExpression = QASMNodeVisitor.visitUnaryExpression
OpenPulseNodeVisitor.visitWhileStatement = QASMNodeVisitor.visitWhileStatement
