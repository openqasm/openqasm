"""
=============================
Parser (``openqasm3.parser``)
=============================

Tools for parsing OpenQASM 3 programs into the :obj:`reference AST <openqasm3.ast>`.

The quick-start interface is simply to call ``openqasm3.parse``:

.. currentmodule:: openqasm3
.. autofunction:: openqasm3.parse

The rest of this module provides some lower-level internals of the parser.

.. currentmodule:: openqasm3.parser
.. autofunction:: span
.. autofunction:: add_span
.. autofunction:: combine_span
.. autofunction:: get_span
.. autoclass:: QASMNodeVisitor
"""

# pylint: disable=wrong-import-order

__all__ = [
    "parse",
    "get_span",
    "add_span",
    "combine_span",
    "span",
    "QASMNodeVisitor",
    "QASM3ParsingError",
]

from contextlib import contextmanager
from typing import Union, TypeVar, List

try:
    from antlr4 import CommonTokenStream, InputStream, ParserRuleContext, RecognitionException
    from antlr4.error.Errors import ParseCancellationException
    from antlr4.error.ErrorStrategy import BailErrorStrategy
    from antlr4.tree.Tree import TerminalNode
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from ._antlr.qasm3Lexer import qasm3Lexer
from ._antlr.qasm3Parser import qasm3Parser
from ._antlr.qasm3ParserVisitor import qasm3ParserVisitor
from . import ast

_TYPE_NODE_INIT = {
    "int": ast.IntType,
    "uint": ast.UintType,
    "float": ast.FloatType,
    "angle": ast.AngleType,
}


class QASM3ParsingError(Exception):
    """An error raised by the AST visitor during the AST-generation phase.  This is raised in cases where the
    given program could not be correctly parsed."""


def parse(input_: str, *, permissive=False) -> ast.Program:
    """
    Parse a complete OpenQASM 3 program from a string.

    :param input_: A string containing a complete OpenQASM 3 program.
    :param permissive: A Boolean controlling whether ANTLR should attempt to
        recover from incorrect input or not.  Defaults to ``False``; if set to
        ``True``, the reference AST produced may be invalid if ANTLR emits any
        warning messages during its parsing phase.
    :return: A complete :obj:`~ast.Program` node.
    """
    lexer = qasm3Lexer(InputStream(input_))
    stream = CommonTokenStream(lexer)
    parser = qasm3Parser(stream)
    if not permissive:
        # For some reason, the Python 3 runtime for ANTLR 4 is missing the
        # setter method `setErrorHandler`, so we have to set the attribute
        # directly.
        parser._errHandler = BailErrorStrategy()
    try:
        tree = parser.program()
    except (RecognitionException, ParseCancellationException) as exc:
        raise QASM3ParsingError() from exc
    return QASMNodeVisitor().visitProgram(tree)


def get_span(node: Union[ParserRuleContext, TerminalNode]) -> ast.Span:
    """Get the span of a node"""
    if isinstance(node, ParserRuleContext):
        return ast.Span(node.start.line, node.start.column, node.stop.line, node.stop.column)
    else:
        return ast.Span(node.symbol.line, node.symbol.start, node.symbol.line, node.symbol.stop)


_NodeT = TypeVar("_NodeT", bound=ast.QASMNode)


def add_span(node: _NodeT, span: ast.Span) -> _NodeT:
    """Set the span of a node and return the node"""
    node.span = span
    return node


def combine_span(first: ast.Span, second: ast.Span):
    """Combine two spans and return the combined one"""
    return ast.Span(first.start_line, first.start_column, second.start_line, second.start_column)


def span(func):
    """Function decorator to automatic attach span to nodes for visit* methods."""

    def wrapped(*args, **kwargs):
        span = get_span(args[1])  # args[1] is ctx
        node = func(*args, **kwargs)
        if node is None:
            raise ValueError(f"None encountered at {span}")
        return add_span(node, span)

    return wrapped


def _visit_identifier(identifier: TerminalNode):
    return add_span(ast.Identifier(identifier.getText()), get_span(identifier))


def _raise_from_context(ctx: ParserRuleContext, message: str):
    raise QASM3ParsingError(f"L{ctx.start.line}:C{ctx.start.column}: {message}")


class QASMNodeVisitor(qasm3ParserVisitor):
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
        return isinstance(self._current_base_scope(), qasm3Parser.GateStatementContext)

    def _in_subroutine(self):
        return isinstance(self._current_base_scope(), qasm3Parser.DefStatementContext)

    def _in_loop(self):
        return any(
            isinstance(scope, (qasm3Parser.ForStatementContext, qasm3Parser.WhileStatementContext))
            for scope in reversed(self._current_context())
        )

    def _parse_scoped_statements(
        self, node: Union[qasm3Parser.ScopeContext, qasm3Parser.StatementOrScopeContext]
    ) -> List[ast.Statement]:
        with self._push_scope(node.parentCtx):
            block = self.visit(node)
            return block.statements if isinstance(block, ast.CompoundStatement) else [block]

    @span
    def visitProgram(self, ctx: qasm3Parser.ProgramContext):
        with self._push_context(ctx):
            version = ctx.version().VersionSpecifier().getText() if ctx.version() else None
            statements = [self.visit(statement) for statement in ctx.statementOrScope()]
            return ast.Program(statements=statements, version=version)

    @span
    def visitStatement(self, ctx: qasm3Parser.StatementContext):
        if ctx.pragma():
            return self.visit(ctx.pragma())
        out = self.visit(ctx.getChild(-1))
        out.annotations = [self.visit(annotation) for annotation in ctx.annotation()]
        return out

    @span
    def visitAnnotation(self, ctx: qasm3Parser.AnnotationContext):
        return ast.Annotation(
            keyword=ctx.AnnotationKeyword().getText()[1:],
            command=ctx.RemainingLineContent().getText() if ctx.RemainingLineContent() else None,
        )

    @span
    def visitScope(self, ctx: qasm3Parser.ScopeContext) -> List[ast.Statement]:
        return ast.CompoundStatement(
            statements=[self.visit(statement) for statement in ctx.statementOrScope()]
        )

    @span
    def visitPragma(self, ctx: qasm3Parser.PragmaContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "pragmas must be global")
        return ast.Pragma(
            command=ctx.RemainingLineContent().getText() if ctx.RemainingLineContent() else None
        )

    @span
    def visitAliasDeclarationStatement(self, ctx: qasm3Parser.AliasDeclarationStatementContext):
        return ast.AliasStatement(
            target=_visit_identifier(ctx.Identifier()),
            value=self.visit(ctx.aliasExpression()),
        )

    @span
    def visitAssignmentStatement(self, ctx: qasm3Parser.AssignmentStatementContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot assign to classical parameters in a gate")
        if ctx.measureExpression():
            return ast.QuantumMeasurementStatement(
                measure=self.visit(ctx.measureExpression()),
                target=self.visit(ctx.indexedIdentifier()),
            )
        return ast.ClassicalAssignment(
            lvalue=self.visit(ctx.indexedIdentifier()),
            op=ast.AssignmentOperator[ctx.op.text],
            rvalue=self.visit(ctx.expression()),
        )

    @span
    def visitBarrierStatement(self, ctx: qasm3Parser.BarrierStatementContext):
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        return ast.QuantumBarrier(qubits=qubits)

    @span
    def visitBoxStatement(self, ctx: qasm3Parser.BoxStatementContext):
        return ast.Box(
            duration=self.visit(ctx.designator()) if ctx.designator() else None,
            body=self._parse_scoped_statements(ctx.scope()),
        )

    @span
    def visitBreakStatement(self, ctx: qasm3Parser.BreakStatementContext):
        if not self._in_loop():
            _raise_from_context(ctx, "'break' statement outside loop")
        return ast.BreakStatement()

    @span
    def visitCalStatement(self, ctx: qasm3Parser.CalStatementContext):
        return ast.CalibrationStatement(
            body=ctx.CalibrationBlock().getText() if ctx.CalibrationBlock() else ""
        )

    @span
    def visitCalibrationGrammarStatement(self, ctx: qasm3Parser.CalibrationGrammarStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "'defcalgrammar' statements must be global")
        return ast.CalibrationGrammarDeclaration(name=ctx.StringLiteral().getText()[1:-1])

    @span
    def visitClassicalDeclarationStatement(
        self, ctx: qasm3Parser.ClassicalDeclarationStatementContext
    ):
        if self._in_gate():
            _raise_from_context(ctx, "cannot declare classical variables in a gate")
        if ctx.arrayType() and not self._in_global_scope():
            _raise_from_context(ctx, "arrays can only be declared globally")
        init = self.visit(ctx.declarationExpression()) if ctx.declarationExpression() else None
        return ast.ClassicalDeclaration(
            type=self.visit(ctx.scalarType() or ctx.arrayType()),
            identifier=_visit_identifier(ctx.Identifier()),
            init_expression=init,
        )

    @span
    def visitConstDeclarationStatement(self, ctx: qasm3Parser.ConstDeclarationStatementContext):
        return ast.ConstantDeclaration(
            type=self.visit(ctx.scalarType()),
            identifier=_visit_identifier(ctx.Identifier()),
            init_expression=self.visit(ctx.declarationExpression()),
        )

    @span
    def visitContinueStatement(self, ctx: qasm3Parser.ContinueStatementContext):
        if not self._in_loop():
            _raise_from_context(ctx, "'continue' statement outside loop")
        return ast.ContinueStatement()

    @span
    def visitDefStatement(self, ctx: qasm3Parser.DefStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "subroutine definitions must be global")
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [self.visit(argument) for argument in ctx.argumentDefinitionList().argumentDefinition()]
            if ctx.argumentDefinitionList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )
        with self._push_context(ctx):
            body = self._parse_scoped_statements(ctx.scope())
        return ast.SubroutineDefinition(
            name=name, arguments=arguments, body=body, return_type=return_type
        )

    @span
    def visitDefcalStatement(self, ctx: qasm3Parser.DefcalStatementContext):
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
            body=ctx.CalibrationBlock().getText() if ctx.CalibrationBlock() else "",
        )

    @span
    def visitDelayStatement(self, ctx: qasm3Parser.DelayStatementContext):
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        return ast.DelayInstruction(duration=self.visit(ctx.designator()), qubits=qubits)

    @span
    def visitEndStatement(self, _: qasm3Parser.EndStatementContext):
        return ast.EndStatement()

    @span
    def visitExpressionStatement(self, ctx: qasm3Parser.ExpressionStatementContext):
        return ast.ExpressionStatement(self.visit(ctx.expression()))

    @span
    def visitExternStatement(self, ctx: qasm3Parser.ExternStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "extern declarations must be global")
        arguments = (
            [self.visit(type) for type in ctx.externArgumentList().externArgument()]
            if ctx.externArgumentList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().scalarType()) if ctx.returnSignature() else None
        )
        return ast.ExternDeclaration(
            name=_visit_identifier(ctx.Identifier()),
            arguments=arguments,
            return_type=return_type,
        )

    @span
    def visitForStatement(self, ctx: qasm3Parser.ForStatementContext):
        if ctx.setExpression():
            set_declaration = self.visit(ctx.setExpression())
        elif ctx.rangeExpression():
            set_declaration = self.visit(ctx.rangeExpression())
        else:
            set_declaration = self.visit(ctx.expression())
        block = self._parse_scoped_statements(ctx.body)
        return ast.ForInLoop(
            type=self.visit(ctx.scalarType()),
            identifier=_visit_identifier(ctx.Identifier()),
            set_declaration=set_declaration,
            block=block,
        )

    @span
    def visitGateCallStatement(self, ctx: qasm3Parser.GateCallStatementContext):
        modifiers = [self.visit(modifier) for modifier in ctx.gateModifier()]
        arguments = (
            [self.visit(argument) for argument in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        qubits = (
            [self.visit(operand) for operand in ctx.gateOperandList().gateOperand()]
            if ctx.gateOperandList()
            else []
        )
        if ctx.GPHASE():
            if len(arguments) != 1:
                _raise_from_context(
                    ctx, f"'gphase' takes exactly one argument, but received {arguments}"
                )
            return ast.QuantumPhase(modifiers=modifiers, argument=arguments[0], qubits=qubits)
        return ast.QuantumGate(
            modifiers=modifiers,
            name=_visit_identifier(ctx.Identifier()),
            arguments=arguments,
            qubits=qubits,
            duration=self.visit(ctx.designator()) if ctx.designator() else None,
        )

    @span
    def visitGateStatement(self, ctx: qasm3Parser.GateStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "gate definitions must be global")
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [_visit_identifier(id_) for id_ in ctx.params.Identifier()]
            if ctx.params is not None
            else []
        )
        qubits = [_visit_identifier(id_) for id_ in ctx.qubits.Identifier()]
        with self._push_context(ctx):
            body = self._parse_scoped_statements(ctx.scope())
        return ast.QuantumGateDefinition(name, arguments, qubits, body)

    @span
    def visitIfStatement(self, ctx: qasm3Parser.IfStatementContext):
        if_body = self._parse_scoped_statements(ctx.if_body)
        else_body = self._parse_scoped_statements(ctx.else_body) if ctx.else_body else []
        return ast.BranchingStatement(
            condition=self.visit(ctx.expression()), if_block=if_body, else_block=else_body
        )

    @span
    def visitIncludeStatement(self, ctx: qasm3Parser.IncludeStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "'include' statements must be global")
        return ast.Include(filename=ctx.StringLiteral().getText()[1:-1])

    @span
    def visitIoDeclarationStatement(self, ctx: qasm3Parser.IoDeclarationStatementContext):
        if not self._in_global_scope():
            keyword = "input" if ctx.INPUT() else "output"
            _raise_from_context(ctx, f"'{keyword}' declarations must be global")
        return ast.IODeclaration(
            io_identifier=ast.IOKeyword.input if ctx.INPUT() else ast.IOKeyword.output,
            type=self.visit(ctx.scalarType()),
            identifier=_visit_identifier(ctx.Identifier()),
        )

    @span
    def visitMeasureArrowAssignmentStatement(
        self, ctx: qasm3Parser.MeasureArrowAssignmentStatementContext
    ):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'measure' instruction in a gate")
        return ast.QuantumMeasurementStatement(
            measure=self.visit(ctx.measureExpression()),
            target=self.visit(ctx.indexedIdentifier()) if ctx.indexedIdentifier() else None,
        )

    @span
    def visitOldStyleDeclarationStatement(
        self, ctx: qasm3Parser.OldStyleDeclarationStatementContext
    ):
        identifier = _visit_identifier(ctx.Identifier())
        size = self.visit(ctx.designator()) if ctx.designator() else None
        if ctx.QREG():
            if not self._in_global_scope():
                _raise_from_context(ctx, "qubit declarations must be global")
            return ast.QubitDeclaration(qubit=identifier, size=size)
        span = (
            combine_span(get_span(ctx.CREG()), get_span(ctx.designator()))
            if ctx.designator()
            else get_span(ctx.CREG())
        )
        return ast.ClassicalDeclaration(
            type=add_span(ast.BitType(size=size), span),
            identifier=identifier,
            init_expression=None,
        )

    @span
    def visitQuantumDeclarationStatement(self, ctx: qasm3Parser.QuantumDeclarationStatementContext):
        if not self._in_global_scope():
            _raise_from_context(ctx, "qubit declarations must be global")
        size_designator = ctx.qubitType().designator()
        return ast.QubitDeclaration(
            qubit=_visit_identifier(ctx.Identifier()),
            size=self.visit(size_designator) if size_designator is not None else None,
        )

    @span
    def visitResetStatement(self, ctx: qasm3Parser.ResetStatementContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'reset' instruction in a gate")
        return ast.QuantumReset(qubits=self.visit(ctx.gateOperand()))

    @span
    def visitReturnStatement(self, ctx: qasm3Parser.ReturnStatementContext):
        if not self._in_subroutine():
            _raise_from_context(ctx, "'return' statement outside subroutine")
        if ctx.expression():
            expression = self.visit(ctx.expression())
        elif ctx.measureExpression():
            expression = self.visit(ctx.measureExpression())
        else:
            expression = None
        return ast.ReturnStatement(expression=expression)

    @span
    def visitSwitchStatement(self, ctx: qasm3Parser.SwitchStatementContext):
        target = self.visit(ctx.expression())
        cases = []
        default = None
        for case in ctx.switchCaseItem():
            if case.CASE():
                if default is not None:
                    _raise_from_context(case, "'case' statement after 'default'")
                values = []
                for expr in case.expressionList().expression():
                    # This AST-generation step does not perform constant folding to validate that
                    # only distinct integers are encountered; we leave that to a later step.
                    values.append(self.visit(expr))
                cases.append((values, self.visit(case.scope())))
            elif default is not None:
                _raise_from_context(case, "multiple 'default' cases")
            else:
                default = self.visit(case.scope())
        return ast.SwitchStatement(target=target, cases=cases, default=default)

    @span
    def visitWhileStatement(self, ctx: qasm3Parser.WhileStatementContext):
        block = self._parse_scoped_statements(ctx.body)
        return ast.WhileLoop(while_condition=self.visit(ctx.expression()), block=block)

    @span
    def visitParenthesisExpression(self, ctx: qasm3Parser.ParenthesisExpressionContext):
        return self.visit(ctx.expression())

    @span
    def visitIndexExpression(self, ctx: qasm3Parser.IndexExpressionContext):
        return ast.IndexExpression(
            collection=self.visit(ctx.expression()),
            index=self.visit(ctx.indexOperator()),
        )

    @span
    def visitUnaryExpression(self, ctx: qasm3Parser.UnaryExpressionContext):
        return ast.UnaryExpression(
            op=ast.UnaryOperator[ctx.op.text],
            expression=self.visit(ctx.expression()),
        )

    @span
    def _visit_binary_expression(self, ctx: ParserRuleContext):
        return ast.BinaryExpression(
            lhs=self.visit(ctx.expression(0)),
            op=ast.BinaryOperator[ctx.op.text],
            rhs=self.visit(ctx.expression(1)),
        )

    visitPowerExpression = _visit_binary_expression
    visitMultiplicativeExpression = _visit_binary_expression
    visitAdditiveExpression = _visit_binary_expression
    visitBitshiftExpression = _visit_binary_expression
    visitComparisonExpression = _visit_binary_expression
    visitEqualityExpression = _visit_binary_expression
    visitBitwiseAndExpression = _visit_binary_expression
    visitBitwiseXorExpression = _visit_binary_expression
    visitBitwiseOrExpression = _visit_binary_expression
    visitLogicalAndExpression = _visit_binary_expression
    visitLogicalOrExpression = _visit_binary_expression

    @span
    def visitCastExpression(self, ctx: qasm3Parser.CastExpressionContext):
        return ast.Cast(type=self.visit(ctx.getChild(0)), argument=self.visit(ctx.expression()))

    @span
    def visitMeasureExpression(self, ctx: qasm3Parser.MeasureExpressionContext):
        if self._in_gate():
            _raise_from_context(ctx, "cannot have a non-unitary 'measure' instruction in a gate")
        return ast.QuantumMeasurement(qubit=self.visit(ctx.gateOperand()))

    @span
    def visitDurationofExpression(self, ctx: qasm3Parser.DurationofExpressionContext):
        target = self._parse_scoped_statements(ctx.scope())
        return ast.DurationOf(target=target)

    @span
    def visitCallExpression(self, ctx: qasm3Parser.CallExpressionContext):
        name = _visit_identifier(ctx.Identifier())
        arguments = (
            [self.visit(argument) for argument in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        if name.name == "sizeof":
            if len(arguments) not in (1, 2):
                _raise_from_context(ctx, "'sizeof' needs either one or two arguments")
            return ast.SizeOf(
                target=arguments[0],
                index=arguments[1] if len(arguments) == 2 else None,
            )
        return ast.FunctionCall(name=name, arguments=arguments)

    @span
    def visitLiteralExpression(self, ctx: qasm3Parser.LiteralExpressionContext):
        if ctx.Identifier():
            return _visit_identifier(ctx.Identifier())
        if ctx.BinaryIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.BinaryIntegerLiteral().getText(), 2))
        if ctx.OctalIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.OctalIntegerLiteral().getText(), 8))
        if ctx.DecimalIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.DecimalIntegerLiteral().getText(), 10))
        if ctx.HexIntegerLiteral():
            return ast.IntegerLiteral(value=int(ctx.HexIntegerLiteral().getText(), 16))
        if ctx.FloatLiteral():
            return ast.FloatLiteral(value=float(ctx.FloatLiteral().getText()))
        if ctx.ImaginaryLiteral():
            return ast.ImaginaryLiteral(value=float(ctx.ImaginaryLiteral().getText()[:-2]))
        if ctx.BooleanLiteral():
            return ast.BooleanLiteral(value=ctx.BooleanLiteral().getText() == "true")
        if ctx.BitstringLiteral():
            stripped = ctx.BitstringLiteral().getText()[1:-1].replace("_", "")
            return ast.BitstringLiteral(value=int(stripped, 2), width=len(stripped))
        if ctx.TimingLiteral():
            text = ctx.TimingLiteral().getText()
            value, suffix = text[:-2], text[-2:]
            if suffix[1] == "s":
                if suffix[0] in "num":
                    unit = ast.TimeUnit[suffix]
                elif suffix[0] == "µ":
                    unit = ast.TimeUnit["us"]
                else:
                    unit = ast.TimeUnit["s"]
                    value = text[:-1]
            else:
                unit = ast.TimeUnit["dt"]
            return ast.DurationLiteral(value=float(value), unit=unit)
        if ctx.HardwareQubit():
            return ast.Identifier(ctx.HardwareQubit().getText())
        raise _raise_from_context(ctx, "unknown literal type")

    @span
    def visitAliasExpression(self, ctx: qasm3Parser.AliasExpressionContext):
        # This choice in the recursion and the accompanying reversal of the
        # iterator builds the tree as left-associative.  The logical operation
        # is arbitrarily associative, but the AST needs us to make a choice.
        def recurse(previous, iterator):
            rhs = self.visit(previous)
            try:
                current = next(iterator)
            except StopIteration:
                return self.visit(previous)
            lhs = recurse(current, iterator)
            return add_span(ast.Concatenation(lhs=lhs, rhs=rhs), combine_span(lhs.span, rhs.span))

        # This iterator should always be non-empty if ANTLR did its job right.
        iterator = reversed(ctx.expression())
        return recurse(next(iterator), iterator)

    @span
    def visitDeclarationExpression(self, ctx: qasm3Parser.DeclarationExpressionContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitRangeExpression(self, ctx: qasm3Parser.RangeExpressionContext):
        # start, end and step are all optional as in [:]
        # It could be [start:end] or [start:step:end]
        start = None
        end = None
        step = None
        colons_seen = 0

        for child in ctx.getChildren():
            if isinstance(child, qasm3Parser.ExpressionContext):
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
    def visitSetExpression(self, ctx: qasm3Parser.SetExpressionContext):
        return ast.DiscreteSet(values=[self.visit(expression) for expression in ctx.expression()])

    @span
    def visitArrayLiteral(self, ctx: qasm3Parser.ArrayLiteralContext):
        array_literal_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.ArrayLiteralContext,
        )

        def predicate(child):
            return isinstance(child, array_literal_element)

        return ast.ArrayLiteral(
            values=[self.visit(element) for element in ctx.getChildren(predicate=predicate)],
        )

    def visitIndexOperator(self, ctx: qasm3Parser.IndexOperatorContext):
        if ctx.setExpression():
            return self.visit(ctx.setExpression())

        index_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.RangeExpressionContext,
        )

        def predicate(child):
            return isinstance(child, index_element)

        return [self.visit(child) for child in ctx.getChildren(predicate=predicate)]

    @span
    def visitIndexedIdentifier(self, ctx: qasm3Parser.IndexedIdentifierContext):
        if not ctx.indexOperator():
            return _visit_identifier(ctx.Identifier())
        return ast.IndexedIdentifier(
            name=_visit_identifier(ctx.Identifier()),
            indices=[self.visit(index) for index in ctx.indexOperator()],
        )

    @span
    def visitDesignator(self, ctx: qasm3Parser.DesignatorContext):
        return self.visit(ctx.expression())

    @span
    def visitGateModifier(self, ctx: qasm3Parser.GateModifierContext):
        if ctx.INV():
            return ast.QuantumGateModifier(modifier=ast.GateModifierName["inv"], argument=None)
        if ctx.POW():
            return ast.QuantumGateModifier(
                modifier=ast.GateModifierName["pow"], argument=self.visit(ctx.expression())
            )
        return ast.QuantumGateModifier(
            modifier=ast.GateModifierName["ctrl" if ctx.CTRL() else "negctrl"],
            argument=self.visit(ctx.expression()) if ctx.expression() else None,
        )

    @span
    def visitScalarType(self, ctx: qasm3Parser.ScalarTypeContext):
        if ctx.BOOL():
            return ast.BoolType()
        if ctx.DURATION():
            return ast.DurationType()
        if ctx.STRETCH():
            return ast.StretchType()
        if ctx.BIT():
            return ast.BitType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.INT():
            return ast.IntType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.UINT():
            return ast.UintType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.FLOAT():
            return ast.FloatType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.ANGLE():
            return ast.AngleType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        if ctx.COMPLEX():
            base = self.visit(ctx.scalarType()) if ctx.scalarType() else None
            if base is not None and not isinstance(base, ast.FloatType):
                _raise_from_context(ctx.scalarType(), f"invalid type of complex components")
            return ast.ComplexType(base_type=base)
        _raise_from_context(ctx, "unhandled type: {ctx.getText()}")

    @span
    def visitArrayType(self, ctx: qasm3Parser.ArrayTypeContext):
        base = self.visit(ctx.scalarType())
        if not isinstance(
            base,
            (
                ast.BitType,
                ast.IntType,
                ast.UintType,
                ast.FloatType,
                ast.AngleType,
                ast.DurationType,
                ast.BoolType,
                ast.ComplexType,
            ),
        ):
            _raise_from_context(ctx.scalarType(), f"invalid scalar type for array")
        return ast.ArrayType(
            base_type=base,
            dimensions=[self.visit(expression) for expression in ctx.expressionList().expression()],
        )

    @span
    def visitGateOperand(self, ctx: qasm3Parser.GateOperandContext):
        if ctx.HardwareQubit():
            return ast.Identifier(name=ctx.getText())
        return self.visit(ctx.indexedIdentifier())

    @span
    def visitDefcalTarget(self, ctx: qasm3Parser.DefcalTargetContext):
        return ast.Identifier(name=ctx.getText())

    @span
    def visitArgumentDefinition(self, ctx: qasm3Parser.ArgumentDefinitionContext):
        name = _visit_identifier(ctx.Identifier())
        if ctx.qubitType() or ctx.QREG():
            designator = ctx.qubitType().designator() if ctx.qubitType() else ctx.designator()
            return ast.QuantumArgument(
                name=name, size=self.visit(designator) if designator else None
            )
        access = None
        if ctx.CREG():
            size = self.visit(ctx.designator()) if ctx.designator() else None
            creg_span = get_span(ctx.CREG())
            type_ = add_span(
                ast.BitType(size=size),
                combine_span(creg_span, get_span(size)) if size else creg_span,
            )
        elif ctx.arrayReferenceType():
            array_ctx = ctx.arrayReferenceType()
            access = (
                ast.AccessControl.readonly if array_ctx.READONLY() else ast.AccessControl.mutable
            )
            base_type = self.visit(array_ctx.scalarType())
            dimensions = (
                self.visit(array_ctx.expression())
                if array_ctx.expression()
                else [self.visit(expr) for expr in array_ctx.expressionList().expression()]
            )
            type_ = add_span(
                ast.ArrayReferenceType(base_type=base_type, dimensions=dimensions),
                get_span(array_ctx),
            )
        else:
            type_ = self.visit(ctx.scalarType())
        return ast.ClassicalArgument(type=type_, name=name, access=access)

    @span
    def visitDefcalArgumentDefinition(self, ctx: qasm3Parser.DefcalArgumentDefinitionContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitExternArgument(self, ctx: qasm3Parser.ExternArgumentContext):
        access = None
        if ctx.CREG():
            type_ = ast.BitType(size=self.visit(ctx.designator()) if ctx.designator() else None)
        elif ctx.scalarType():
            type_ = self.visit(ctx.scalarType())
        else:
            array_ctx = ctx.arrayReferenceType()
            access = (
                ast.AccessControl.readonly if array_ctx.READONLY() else ast.AccessControl.mutable
            )
            base_type = self.visit(array_ctx.scalarType())
            dimensions = (
                self.visit(array_ctx.expression())
                if array_ctx.expression()
                else [self.visit(expr) for expr in array_ctx.expressionList().expression()]
            )
            type_ = add_span(
                ast.ArrayReferenceType(base_type=base_type, dimensions=dimensions),
                get_span(array_ctx),
            )
        return ast.ExternArgument(type=type_, access=access)

    @span
    def visitDefcalOperand(self, ctx: qasm3Parser.DefcalOperandContext):
        if ctx.HardwareQubit():
            return ast.Identifier(ctx.HardwareQubit().getText())
        return _visit_identifier(ctx.Identifier())

    def visitStatementOrScope(self, ctx: qasm3Parser.StatementOrScopeContext) -> ast.Statement:
        return self.visit(ctx.scope()) if ctx.scope() else self.visit(ctx.statement())
