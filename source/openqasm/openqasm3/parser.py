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
]

from typing import Union, TypeVar

try:
    from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
    from antlr4.tree.Tree import TerminalNode
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from .antlr.qasm3Lexer import qasm3Lexer
from .antlr.qasm3Parser import qasm3Parser
from .antlr.qasm3ParserVisitor import qasm3ParserVisitor
from .ast import (
    AccessControl,
    AliasStatement,
    AngleType,
    ArrayLiteral,
    ArrayReferenceType,
    ArrayType,
    AssignmentOperator,
    BinaryExpression,
    BinaryOperator,
    BitType,
    BoolType,
    BooleanLiteral,
    Box,
    BranchingStatement,
    BreakStatement,
    CalibrationDefinition,
    CalibrationGrammarDeclaration,
    Cast,
    ClassicalArgument,
    ClassicalAssignment,
    ClassicalDeclaration,
    ComplexType,
    Concatenation,
    Constant,
    ConstantDeclaration,
    ConstantName,
    ContinueStatement,
    DelayInstruction,
    DiscreteSet,
    DurationLiteral,
    DurationOf,
    DurationType,
    EndStatement,
    ExpressionStatement,
    ExternDeclaration,
    FloatType,
    ForInLoop,
    FunctionCall,
    GateModifierName,
    IODeclaration,
    IOKeyword,
    Identifier,
    Include,
    IndexExpression,
    IndexedIdentifier,
    IntType,
    IntegerLiteral,
    Pragma,
    Program,
    QASMNode,
    QuantumArgument,
    QuantumBarrier,
    QuantumGate,
    QuantumGateDefinition,
    QuantumGateModifier,
    QuantumMeasurement,
    QuantumMeasurementAssignment,
    QuantumPhase,
    QuantumReset,
    QubitDeclaration,
    RangeDefinition,
    RealLiteral,
    ReturnStatement,
    Span,
    StretchType,
    StringLiteral,
    SubroutineDefinition,
    TimeUnit,
    UintType,
    UnaryExpression,
    UnaryOperator,
    WhileLoop,
)

_TYPE_NODE_INIT = {"int": IntType, "uint": UintType, "float": FloatType, "angle": AngleType}


def parse(input_: str) -> Program:
    """
    Parse a complete OpenQASM 3 program from a string.

    :param input_: A string containing a complete OpenQASM 3 program.
    :return: A complete :obj:`~ast.Program` node.
    """
    lexer = qasm3Lexer(InputStream(input_))
    stream = CommonTokenStream(lexer)
    parser = qasm3Parser(stream)

    tree = parser.program()

    return QASMNodeVisitor().visitProgram(tree)


def get_span(node: Union[ParserRuleContext, TerminalNode]) -> Span:
    """Get the span of a node"""
    if isinstance(node, ParserRuleContext):
        return Span(node.start.line, node.start.column, node.stop.line, node.stop.column)
    else:
        return Span(node.symbol.line, node.symbol.start, node.symbol.line, node.symbol.stop)


_NodeT = TypeVar("_NodeT", bound=QASMNode)


def add_span(node: _NodeT, span: Span) -> _NodeT:
    """Set the span of a node and return the node"""
    node.span = span
    return node


def combine_span(first: Span, second: Span):
    """Combine two spans and return the combined one"""
    return Span(first.start_line, first.start_column, second.start_line, second.start_column)


def span(func):
    """Function decorator to automatic attach span to nodes for visit* methods."""

    def wrapped(*args, **kwargs):
        span = get_span(args[1])  # args[1] is ctx
        node = func(*args, **kwargs)
        if node is None:
            raise ValueError(f"None encountered at {span}")
        else:
            node.span = span
            return node

    return wrapped


class QASMNodeVisitor(qasm3ParserVisitor):
    @span
    def visitProgram(self, ctx: qasm3Parser.ProgramContext):

        version = (
            ctx.header().version().getChild(1).getText()
            if ctx.header() and ctx.header().version()
            else ""
        )

        includes = (
            [self.visitInclude(include) for include in ctx.header().include()]
            if ctx.header() and ctx.header().include()
            else []
        )

        io_variables = []
        if ctx.header() and ctx.header().io():
            io_list = ctx.header().io()
            for io in io_list:
                identifier = add_span(
                    Identifier(io.Identifier().getText()), get_span(io.Identifier())
                )
                ctype = self.visit(io.classicalType())
                io_variables.append(
                    IODeclaration(
                        io_identifier=IOKeyword[io.getChild(0).getText()],
                        type=ctype,
                        identifier=identifier,
                        init_expression=None,
                    )
                )

        statements = []
        for globalStatement in ctx.globalStatement():
            statements.append(self.visit(globalStatement))
        for statement in ctx.statement():
            statements.append(self.visit(statement))
        program = Program(
            statements=sorted(statements, key=lambda x: (x.span.start_line, x.span.start_column))
        )
        program.version = version
        program.io_variables = io_variables
        program.includes = includes

        return program

    @span
    def visitInclude(self, ctx: qasm3Parser.IncludeContext):
        return Include(filename=ctx.getChild(1).getText()[1:-1])

    @span
    def visitGlobalStatement(self, ctx: qasm3Parser.GlobalStatementContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitQuantumGateDefinition(self, ctx: qasm3Parser.QuantumGateDefinitionContext):
        gate_name = self.visit(ctx.quantumGateSignature().quantumGateName())
        gate_arg_lists = ctx.quantumGateSignature().identifierList()  # argument and qubit lists
        arguments = (
            [
                add_span(Identifier(arg.getText()), get_span(arg))
                for arg in gate_arg_lists[0].Identifier()
            ]
            if len(gate_arg_lists) == 2
            else []
        )
        qubits = [
            add_span(Identifier(i.getText()), get_span(i)) for i in gate_arg_lists[-1].Identifier()
        ]
        child_count = ctx.quantumBlock().getChildCount()
        body = [self.visit(ctx.quantumBlock().getChild(i)) for i in range(1, child_count - 1)]
        return QuantumGateDefinition(gate_name, arguments, qubits, body)

    @span
    def visitQuantumGateName(self, ctx: qasm3Parser.QuantumGateNameContext):
        return Identifier(ctx.getText())

    @span
    def visitQuantumLoop(self, ctx: qasm3Parser.QuantumLoopContext):
        if ctx.loopSignature().getChild(0).getText() == "while":
            return WhileLoop(
                while_condition=self.visit(ctx.loopSignature().expression()),
                block=self.visit(ctx.quantumLoopBlock()),
            )
        else:  # For In Loop
            return ForInLoop(
                loop_variable=add_span(
                    Identifier(ctx.loopSignature().Identifier().getText()),
                    get_span(ctx.loopSignature().Identifier()),
                ),
                set_declaration=self.visit(ctx.loopSignature().setDeclaration()),
                block=self.visit(ctx.quantumLoopBlock()),
            )

    def visitQuantumLoopBlock(self, ctx: qasm3Parser.QuantumLoopBlockContext):
        if ctx.LBRACE():
            return [self.visit(statement) for statement in ctx.quantumStatement()]
        else:
            return [self.visit(ctx.quantumStatement())]

    @span
    def visitQuantumDeclarationStatement(self, ctx: qasm3Parser.QuantumDeclarationStatementContext):
        return self.visit(ctx.quantumDeclaration())

    @span
    def visitQuantumDeclaration(self, ctx: qasm3Parser.QuantumDeclarationContext):
        return QubitDeclaration(
            add_span(
                Identifier(
                    ctx.Identifier().getText(),
                ),
                get_span(ctx.Identifier()),
            ),
            self.visit(ctx.designator()) if ctx.designator() else None,
        )

    @span
    def visitDesignator(self, ctx: qasm3Parser.DesignatorContext):
        return self.visit(ctx.expression())

    @span
    def visitStatement(self, ctx: qasm3Parser.StatementContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitAliasStatement(self, ctx: qasm3Parser.AliasStatementContext):
        target = Identifier(name=ctx.Identifier().getText())
        value = self.visit(ctx.aliasInitializer())
        return AliasStatement(target=add_span(target, get_span(ctx.Identifier())), value=value)

    @span
    def visitExpressionStatement(self, ctx: qasm3Parser.ExpressionStatementContext):
        return ExpressionStatement(self.visit(ctx.expression()))

    @span
    def visitEndStatement(self, ctx: qasm3Parser.EndStatementContext):
        return EndStatement()

    @span
    def visitQuantumStatement(self, ctx: qasm3Parser.QuantumStatementContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitQuantumInstruction(self, ctx: qasm3Parser.QuantumInstructionContext):
        quantum_gate_call = ctx.quantumGateCall()
        quantum_phase = ctx.quantumPhase()
        quantum_measurement = ctx.quantumMeasurement()
        quantum_reset = ctx.quantumReset()
        quantum_barrier = ctx.quantumBarrier()
        if quantum_gate_call:
            return self.visit(quantum_gate_call)
        elif quantum_phase:
            return self.visit(quantum_phase)
        elif quantum_measurement:
            return self.visit(quantum_measurement)
        elif quantum_reset:
            return self.visit(quantum_reset)
        elif quantum_barrier:
            return self.visit(quantum_barrier)
        else:
            raise NotImplementedError(
                f"Not implemented QuantumInstructionContext at {get_span(ctx)}"
            )

    @span
    def visitQuantumGateCall(self, ctx: qasm3Parser.QuantumGateCallContext):
        modifiers = [self.visit(modifier) for modifier in ctx.quantumGateModifier()]
        gate_name = self.visit(ctx.quantumGateName())
        expression_list = ctx.expressionList()
        if expression_list:
            arguments = [self.visit(expression) for expression in expression_list.expression()]
        else:
            arguments = []
        qubits = [self.visit(qubit) for qubit in ctx.indexedIdentifier()]

        gate = QuantumGate(modifiers=modifiers, name=gate_name, arguments=arguments, qubits=qubits)

        return gate

    @span
    def visitQuantumPhase(self, ctx: qasm3Parser.QuantumPhaseContext):
        modifiers = [self.visit(modifier) for modifier in ctx.quantumGateModifier()]
        argument = self.visit(ctx.expression())
        qubits = []
        if ctx.indexedIdentifier():
            qubits = [self.visit(qubit) for qubit in ctx.indexedIdentifier()]

        return QuantumPhase(modifiers, argument, qubits)

    @span
    def visitQuantumReset(self, ctx: qasm3Parser.QuantumResetContext):
        return QuantumReset(self.visit(ctx.indexedIdentifier()))

    @span
    def visitQuantumBarrier(self, ctx: qasm3Parser.QuantumBarrierContext):
        qubits = [self.visit(id) for id in ctx.indexedIdentifier()]
        return QuantumBarrier(qubits)

    @span
    def visitQuantumMeasurement(self, ctx: qasm3Parser.QuantumMeasurementContext):
        return QuantumMeasurement(self.visit(ctx.indexedIdentifier()))

    @span
    def visitQuantumMeasurementAssignment(
        self, ctx: qasm3Parser.QuantumMeasurementAssignmentContext
    ):
        return QuantumMeasurementAssignment(
            self.visit(ctx.indexedIdentifier()) if ctx.indexedIdentifier() else None,
            self.visit(ctx.quantumMeasurement()),
        )

    @span
    def visitClassicalDeclarationStatement(
        self, ctx: qasm3Parser.ClassicalDeclarationStatementContext
    ):
        classical_declaration_context = ctx.classicalDeclaration()
        constant_declaration_context = ctx.constantDeclaration()
        if classical_declaration_context:
            return self.visit(classical_declaration_context)
        elif constant_declaration_context:
            return self.visit(ctx.constantDeclaration())
        else:
            raise NotImplementedError(
                f"Not implemented ClassicalDeclarationStatement at {get_span(ctx)}"
            )

    def visitClassicalDeclaration(self, ctx: qasm3Parser.ClassicalDeclarationContext):
        if ctx.singleDesignatorDeclaration():
            return self.visit(ctx.singleDesignatorDeclaration())
        if ctx.noDesignatorDeclaration():
            return self.visit(ctx.noDesignatorDeclaration())
        if ctx.bitDeclaration():
            return self.visit(ctx.bitDeclaration())
        if ctx.complexDeclaration():
            return self.visit(ctx.complexDeclaration())
        if ctx.arrayDeclaration():
            return self.visit(ctx.arrayDeclaration())
        raise NotImplementedError(f"Not implemented ClassicalDeclaration at {get_span(ctx)}")

    @span
    def visitConstantDeclaration(self, ctx: qasm3Parser.ConstantDeclarationContext):
        return ConstantDeclaration(
            type=self.visit(ctx.classicalType()),
            identifier=add_span(
                Identifier(name=ctx.Identifier().getText()), get_span(ctx.Identifier())
            ),
            init_expression=self.visit(ctx.equalsExpression().expression()),
        )

    @span
    def visitNoDesignatorDeclaration(self, ctx: qasm3Parser.NoDesignatorDeclarationContext):
        return ClassicalDeclaration(
            type=self.visit(ctx.noDesignatorType()),
            identifier=add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            init_expression=self.visit(ctx.equalsExpression().expression())
            if ctx.equalsExpression()
            else None,
        )

    @span
    def visitNoDesignatorType(self, ctx: qasm3Parser.NoDesignatorTypeContext):
        type_text = ctx.getText()
        if type_text == "bool":
            return add_span(BoolType(), get_span(ctx))
        elif type_text == "duration":
            return add_span(DurationType(), get_span(ctx))
        else:
            # stretch type
            return add_span(StretchType(), get_span(ctx))

    @span
    def visitSingleDesignatorDeclaration(self, ctx: qasm3Parser.SingleDesignatorDeclarationContext):
        equals_expression = ctx.equalsExpression()
        init_expression = self.visit(equals_expression.expression()) if equals_expression else None

        type_name = ctx.singleDesignatorType().getText()
        if type_name in _TYPE_NODE_INIT:
            type_size = self.visit(ctx.designator())
            type_node = _TYPE_NODE_INIT[type_name](type_size)
        else:
            # To capture potential parser errors.
            raise ValueError(f"Type name {type_name} not found.")

        return ClassicalDeclaration(
            add_span(
                type_node,
                combine_span(get_span(ctx.singleDesignatorType()), get_span(ctx.designator())),
            ),
            add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            init_expression,
        )

    @span
    def visitBitDeclaration(self, ctx: qasm3Parser.BitDeclarationContext):
        equals_expression = ctx.equalsExpression()
        init_expression = self.visit(equals_expression.expression()) if equals_expression else None
        desinator = ctx.designator()
        desinator_expression = self.visit(desinator) if desinator else None

        return ClassicalDeclaration(
            add_span(
                BitType(desinator_expression),
                get_span(ctx),
            ),
            add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            init_expression,
        )

    @span
    def visitComplexDeclaration(self, ctx: qasm3Parser.ComplexDeclarationContext):
        return ClassicalDeclaration(
            add_span(
                ComplexType(base_type=self.visit(ctx.numericType())),
                get_span(ctx),
            ),
            add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            self.visit(ctx.equalsExpression().expression()) if ctx.equalsExpression() else None,
        )

    @span
    def visitArrayDeclaration(self, ctx: qasm3Parser.ArrayDeclarationContext):
        if ctx.arrayInitializer():
            initializer = self.visit(ctx.arrayInitializer())
        elif ctx.expression():
            initializer = self.visit(ctx.expression())
        else:
            initializer = None
        return ClassicalDeclaration(
            self.visit(ctx.arrayType()),
            add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier())),
            initializer,
        )

    @span
    def visitAssignmentStatement(self, ctx: qasm3Parser.AssignmentStatementContext):
        classical_assignment = ctx.classicalAssignment()
        quantum_measurement_assignment = ctx.quantumMeasurementAssignment()
        if classical_assignment:
            return self.visit(classical_assignment)
        elif quantum_measurement_assignment:
            return self.visit(quantum_measurement_assignment)
        else:
            raise NotImplementedError(f"Not implemented AssignmentStatement at {get_span(ctx)}")

    @span
    def visitQuantumGateModifier(self, ctx: qasm3Parser.QuantumGateModifierContext):
        powModifier = ctx.powModifier()
        ctrlModifier = ctx.ctrlModifier()
        if powModifier:
            modifier = GateModifierName[powModifier.getChild(0).getText()]
            expression = powModifier.expression()
        elif ctrlModifier:
            modifier = GateModifierName[ctrlModifier.getChild(0).getText()]
            expression = ctrlModifier.expression()
        else:
            modifier = GateModifierName[ctx.getChild(0).getText()]
            expression = None

        modifier_expression = self.visit(expression) if expression else None
        return QuantumGateModifier(modifier, modifier_expression)

    def visit(self, tree):
        try:
            return super().visit(tree)
        except:
            raise

    @span
    def visitExpressionTerminator(self, ctx: qasm3Parser.ExpressionTerminatorContext):
        if ctx.Constant():
            const_text = ctx.Constant().getText()
            if const_text == "π":
                const_name = ConstantName.pi
            elif const_text == "𝜏":
                const_name = ConstantName.tau
            elif const_text == "ℇ":
                const_name = ConstantName.euler
            else:
                const_name = ConstantName[const_text]
            return Constant(const_name)
        if ctx.Integer():
            return IntegerLiteral(int(ctx.Integer().getText()))
        if ctx.RealNumber():
            return RealLiteral(float(ctx.RealNumber().getText()))
        if ctx.BooleanLiteral():
            return BooleanLiteral(ctx.BooleanLiteral().getText() == "true")
        if ctx.Identifier():
            return Identifier(ctx.Identifier().getText())
        if ctx.StringLiteral():
            return StringLiteral(ctx.StringLiteral().getText()[1:-1])
        if ctx.builtInCall():
            return self.visit(ctx.builtInCall())
        if ctx.externOrSubroutineCall():
            return self.visit(ctx.externOrSubroutineCall())
        if ctx.timingIdentifier():
            return self.visit(ctx.timingIdentifier())
        return self.visit(ctx.expression())

    @span
    def visitArrayInitializer(self, ctx: qasm3Parser.ArrayInitializerContext):
        array_literal_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.ArrayInitializerContext,
        )

        def predicate(child):
            return isinstance(child, array_literal_element)

        return ArrayLiteral(
            values=[self.visit(element) for element in ctx.getChildren(predicate=predicate)],
        )

    @span
    def visitTimingIdentifier(self, ctx: qasm3Parser.TimingIdentifierContext):
        if ctx.TimingLiteral():
            # parse timing literal
            s = ctx.TimingLiteral().getText()
            if s[-2:] in ["dt", "ns", "us", "ms"]:
                duration_literal = DurationLiteral(float(s[:-2]), TimeUnit[s[-2:]])
            elif s[-2:] == "µs":
                duration_literal = DurationLiteral(float(s[:-2]), TimeUnit["us"])
            else:
                # Must be "s"
                duration_literal = DurationLiteral(float(s[:-1]), TimeUnit["s"])
            return duration_literal
        elif ctx.Identifier():
            return DurationOf(
                target=add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
            )
        else:
            child_count = ctx.quantumBlock().getChildCount()
            return DurationOf(
                target=[
                    self.visit(ctx.quantumBlock().getChild(i)) for i in range(1, child_count - 1)
                ]
            )

    @span
    def visitUnaryExpression(self, ctx: qasm3Parser.UnaryExpressionContext):
        if ctx.unaryOperator():
            return UnaryExpression(
                UnaryOperator[ctx.unaryOperator().getText()],
                self.visit(ctx.powerExpression()),
            )
        return self.visit(ctx.powerExpression())

    @span
    def visitBuiltInCall(self, ctx: qasm3Parser.BuiltInCallContext):
        if ctx.BuiltinMath():
            return FunctionCall(
                add_span(Identifier(ctx.BuiltinMath().getText()), get_span(ctx.BuiltinMath())),
                [self.visit(expression) for expression in ctx.expressionList().expression()],
            )
        if ctx.SIZEOF():
            return FunctionCall(
                add_span(Identifier(name=ctx.SIZEOF().getText()), get_span(ctx.SIZEOF())),
                [self.visit(expression) for expression in ctx.expressionList().expression()],
            )
        if ctx.castOperator():
            return Cast(
                self.visit(ctx.castOperator().classicalType()),
                [self.visit(expression) for expression in ctx.expressionList().expression()],
            )

    @span
    def visitExternDeclaration(self, ctx: qasm3Parser.ExternDeclarationContext):
        classical_types = (
            [
                self.visit(classical_type)
                for classical_type in ctx.classicalTypeList().classicalType()
            ]
            if ctx.classicalTypeList()
            else []
        )
        return_type = (
            self.visit(ctx.returnSignature().classicalType()) if ctx.returnSignature() else None
        )
        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        return ExternDeclaration(
            name=name,
            classical_types=classical_types,
            return_type=return_type,
        )

    @span
    def visitExternOrSubroutineCall(self, ctx: qasm3Parser.ExternOrSubroutineCallContext):
        expressions = (
            [self.visit(expression) for expression in ctx.expressionList().expression()]
            if ctx.expressionList()
            else []
        )
        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        return FunctionCall(name, expressions)

    @span
    def visitExpression(self, ctx: qasm3Parser.ExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitLogicalAndExpression(self, ctx: qasm3Parser.LogicalAndExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitBitOrExpression(self, ctx: qasm3Parser.BitOrExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitXOrExpression(self, ctx: qasm3Parser.XOrExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitBitAndExpression(self, ctx: qasm3Parser.BitAndExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitEqualityExpression(self, ctx: qasm3Parser.EqualityExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitComparisonExpression(self, ctx: qasm3Parser.ComparisonExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitBitShiftExpression(self, ctx: qasm3Parser.BitShiftExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitAdditiveExpression(self, ctx: qasm3Parser.AdditiveExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitMultiplicativeExpression(self, ctx: qasm3Parser.MultiplicativeExpressionContext):
        return self._visitBinaryExpression(ctx)

    @span
    def visitPowerExpression(self, ctx: qasm3Parser.PowerExpressionContext):
        return self._visitBinaryExpression(ctx)

    def _visitBinaryExpression(self, ctx: ParserRuleContext):
        """
        All binary expressions fit this patten so we refactored the code
        """
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))
        else:
            return BinaryExpression(
                op=BinaryOperator[ctx.getChild(1).getText()],
                lhs=self.visit(ctx.getChild(0)),
                rhs=self.visit(ctx.getChild(2)),
            )

    @span
    def visitAliasInitializer(self, ctx: qasm3Parser.AliasInitializerContext):
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
            return add_span(Concatenation(lhs=lhs, rhs=rhs), combine_span(lhs.span, rhs.span))

        # This iterator should always be non-empty if ANTLR did its job right.
        iterator = reversed(ctx.expression())
        return recurse(next(iterator), iterator)

    @span
    def visitIndexExpression(self, ctx: qasm3Parser.IndexExpressionContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))
        return IndexExpression(
            collection=self.visit(ctx.indexExpression()),
            index=self.visit(ctx.indexOperator()),
        )

    @span
    def visitIndexedIdentifier(self, ctx: qasm3Parser.IndexedIdentifierContext):
        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        if not ctx.indexOperator():
            return name
        indices = [self.visit(operator) for operator in ctx.indexOperator()]
        return IndexedIdentifier(name=name, indices=indices)

    def visitIndexOperator(self, ctx: qasm3Parser.IndexOperatorContext):
        if ctx.discreteSet():
            return self.visit(ctx.discreteSet())

        index_element = (
            qasm3Parser.ExpressionContext,
            qasm3Parser.RangeDefinitionContext,
        )

        def predicate(child):
            return isinstance(child, index_element)

        return [self.visit(child) for child in ctx.getChildren(predicate=predicate)]

    @span
    def visitCalibrationGrammarDeclaration(
        self, ctx: qasm3Parser.CalibrationGrammarDeclarationContext
    ):
        return CalibrationGrammarDeclaration(
            calibration_grammar=ctx.StringLiteral().getText()[1:-1]
        )

    @span
    def visitCalibrationDefinition(self, ctx: qasm3Parser.CalibrationDefinitionContext):
        # TODO: Possible grammar improvement. The current grammar return the body as a token
        # stream. We reconstruct the body by concat the tokens space delimiter.
        # This will not exactly reproduce the body but it can be parsed by another grammar.
        body_chars = []  # Python concatenation is slow so we build a list first
        for i in range(ctx.getChildCount() - 2, 0, -1):
            node = ctx.getChild(i)
            if isinstance(node, TerminalNode):
                body_chars.insert(0, node.getText())
            else:
                break

        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
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
            body=" ".join(body_chars[1:]),
        )

    def visitClassicalArgumentList(self, ctx: qasm3Parser.ClassicalArgumentListContext):
        return [self.visit(argument) for argument in ctx.classicalArgument()]

    @span
    def visitClassicalArgument(self, ctx: qasm3Parser.ClassicalArgumentContext):
        if ctx.CONST():
            access = AccessControl.CONST
        elif ctx.MUTABLE():
            access = AccessControl.MUTABLE
        else:
            access = None

        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_size = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_size)
            else:
                # To capture potential parser error.
                raise ValueError("Type name {type_name} not found.")

            classical_type = add_span(
                type_node,
                combine_span(get_span(ctx.singleDesignatorType()), get_span(ctx.designator())),
            )

        elif ctx.noDesignatorType():
            classical_type = self.visit(ctx.noDesignatorType())

        elif ctx.COMPLEX():
            classical_type = add_span(
                ComplexType(base_type=self.visit(ctx.numericType())),
                combine_span(get_span(ctx.COMPLEX()), get_span(ctx.RBRACKET())),
            )

        elif ctx.arrayReferenceType():
            classical_type = self.visit(ctx.arrayReferenceType())

        else:
            classical_type = add_span(
                BitType(
                    self.visit(ctx.designator()) if ctx.designator() else None,
                ),
                get_span(ctx.getChild(0)),
            )

        identifier = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        return ClassicalArgument(
            type=classical_type,
            name=identifier,
            access=access,
        )

    def visitExpressionList(self, ctx: qasm3Parser.ExpressionListContext):
        return [self.visit(expression) for expression in ctx.expression()]

    @span
    def visitNonArrayType(self, ctx: qasm3Parser.NonArrayTypeContext):
        # TODO: due to the way classical argument is declared, there some duplication
        # Consider refactor classical argument grammar
        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_size = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_size)
            else:
                # To capture potential parser errors.
                raise ValueError(f"Type name {type_name} not found.")

            return add_span(
                type_node,
                combine_span(get_span(ctx.singleDesignatorType()), get_span(ctx.designator())),
            )

        elif ctx.noDesignatorType():
            return self.visit(ctx.noDesignatorType())
        elif ctx.bitType():
            return BitType(
                self.visit(ctx.designator()) if ctx.designator() else None,
            )
        elif ctx.numericType():
            return ComplexType(base_type=self.visit(ctx.numericType()))

    @span
    def visitArrayType(self, ctx: qasm3Parser.ArrayTypeContext):
        return ArrayType(
            base_type=self.visit(ctx.nonArrayType()),
            dimensions=[self.visit(expression) for expression in ctx.expressionList().expression()],
        )

    @span
    def visitArrayReferenceType(self, ctx: qasm3Parser.ArrayReferenceTypeContext):
        dimension_ctx = ctx.arrayReferenceTypeDimensionSpecifier()
        if dimension_ctx.DIM():
            dimensions = self.visit(dimension_ctx.expression())
        else:
            dimensions = [
                self.visit(expression) for expression in dimension_ctx.expressionList().expression()
            ]
        return ArrayReferenceType(base_type=self.visit(ctx.nonArrayType()), dimensions=dimensions)

    @span
    def visitNumericType(self, ctx: qasm3Parser.NumericTypeContext):
        # TODO: This method has significant duplication with visitClassicalType
        # Need to refactor the syntax.
        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_size = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_size)
            else:
                # To capture potential parser errors.
                raise ValueError(f"Type name {type_name} not found.")

            return add_span(
                type_node,
                combine_span(get_span(ctx.singleDesignatorType()), get_span(ctx.designator())),
            )

    @span
    def visitSubroutineDefinition(self, ctx: qasm3Parser.SubroutineDefinitionContext):
        name = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        return SubroutineDefinition(
            name=name,
            arguments=[
                self.visit(argument) for argument in ctx.anyTypeArgumentList().anyTypeArgument()
            ]
            if ctx.anyTypeArgumentList()
            else [],
            return_type=self.visit(ctx.returnSignature().classicalType())
            if ctx.returnSignature()
            else None,
            body=self.visit(ctx.subroutineBlock()),
        )

    @span
    def visitAnyTypeArgument(self, ctx: qasm3Parser.AnyTypeArgumentContext):
        return self.visit(ctx.getChild(0))

    def visitSubroutineBlock(self, ctx: qasm3Parser.SubroutineBlockContext):
        statements = [self.visit(statement) for statement in ctx.statement()]
        if ctx.returnStatement():
            statements.append(self.visit(ctx.returnStatement()))

        return statements

    @span
    def visitPragma(self, ctx: qasm3Parser.PragmaContext):
        return Pragma(statements=[self.visit(st) for st in ctx.statement()])

    @span
    def visitReturnStatement(self, ctx: qasm3Parser.ReturnStatementContext):
        return ReturnStatement(
            expression=self.visit(ctx.getChild(1)) if ctx.getChildCount() > 1 else None
        )

    @span
    def visitQuantumArgument(self, ctx: qasm3Parser.QuantumArgumentContext):
        return QuantumArgument(
            add_span(
                Identifier(
                    ctx.Identifier().getText(),
                ),
                get_span(ctx.Identifier()),
            ),
            self.visit(ctx.designator()) if ctx.designator() else None,
        )

    @span
    def visitBranchingStatement(self, ctx: qasm3Parser.BranchingStatementContext):
        return BranchingStatement(
            condition=self.visit(ctx.expression()),
            if_block=self.visit(ctx.programBlock()[0]),
            else_block=self.visit(ctx.programBlock()[1]) if ctx.getChildCount() > 5 else [],
        )

    def visitProgramBlock(self, ctx: qasm3Parser.ProgramBlockContext):
        if ctx.LBRACE():
            return [self.visit(statement) for statement in list(ctx.getChildren())[1:-1]]
        else:
            return [self.visit(ctx.getChild(0))]

    @span
    def visitControlDirective(self, ctx: qasm3Parser.ControlDirectiveContext):
        if ctx.returnStatement():
            return self.visit(ctx.returnStatement())
        elif ctx.getChild(0).getText() == "break":
            return BreakStatement()
        elif ctx.getChild(0).getText() == "continue":
            return ContinueStatement()
        elif ctx.getChild(0).getText() == "end":
            return EndStatement()

    @span
    def visitLoopStatement(self, ctx: qasm3Parser.LoopStatementContext):
        if ctx.loopSignature().getChild(0).getText() == "while":
            return WhileLoop(
                while_condition=self.visit(ctx.loopSignature().expression()),
                block=self.visit(ctx.programBlock()),
            )
        else:  # For In Loop
            return ForInLoop(
                loop_variable=add_span(
                    Identifier(ctx.loopSignature().Identifier().getText()),
                    get_span(ctx.loopSignature().Identifier()),
                ),
                set_declaration=self.visit(ctx.loopSignature().setDeclaration()),
                block=self.visit(ctx.programBlock()),
            )

    @span
    def visitSetDeclaration(self, ctx: qasm3Parser.SetDeclarationContext):
        if ctx.Identifier():
            return Identifier(name=ctx.Identifier().getText())
        if ctx.rangeDefinition():
            return self.visit(ctx.rangeDefinition())
        return self.visit(ctx.discreteSet())

    @span
    def visitRangeDefinition(self, ctx: qasm3Parser.RangeDefinitionContext):
        # start, end, are all optional as in [:]
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

        return RangeDefinition(start=start, end=end, step=step)

    @span
    def visitDiscreteSet(self, ctx: qasm3Parser.DiscreteSetContext):
        return DiscreteSet(
            values=[self.visit(expression) for expression in ctx.expression()],
        )

    @span
    def visitTimingStatement(self, ctx: qasm3Parser.TimingStatementContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitTimingInstruction(self, ctx: qasm3Parser.TimingInstructionContext):
        return DelayInstruction(
            arguments=[self.visit(expression) for expression in ctx.expressionList().expression()]
            if ctx.expressionList()
            else [],
            duration=self.visit(ctx.designator()),
            qubits=[self.visit(qubit) for qubit in ctx.indexedIdentifier()],
        )

    @span
    def visitTimingBox(self, ctx: qasm3Parser.TimingBoxContext):

        child_count = ctx.quantumBlock().getChildCount()
        return Box(
            duration=self.visit(ctx.designator()) if ctx.designator() else None,
            body=[self.visit(ctx.quantumBlock().getChild(i)) for i in range(1, child_count - 1)],
        )

    @span
    def visitClassicalAssignment(self, ctx: qasm3Parser.ClassicalAssignmentContext):
        return ClassicalAssignment(
            lvalue=self.visit(ctx.indexedIdentifier()),
            op=AssignmentOperator[ctx.assignmentOperator().getText()],
            rvalue=self.visit(ctx.expression()),
        )
