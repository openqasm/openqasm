from typing import Union
import warnings

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
from antlr4.tree.Tree import TerminalNode

from .qasm3Lexer import qasm3Lexer
from .qasm3Parser import qasm3Parser
from .qasm3Visitor import qasm3Visitor
from openqasm.ast import (
    AliasStatement,
    AngleType,
    AssignmentOperator,
    BinaryExpression,
    BinaryOperator,
    BitType,
    BooleanLiteral,
    BoolType,
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
    ConstantDeclaration,
    Constant,
    Concatenation,
    ConstantDeclaration,
    ConstantName,
    ContinueStatement,
    DelayInstruction,
    DurationOf,
    DurationType,
    EndStatement,
    ExpressionStatement,
    ExternDeclaration,
    FloatType,
    ForInLoop,
    FunctionCall,
    GateModifierName,
    Identifier,
    Include,
    IndexExpression,
    IntegerLiteral,
    IntType,
    IODeclaration,
    IOKeyword,
    OpenNode,
    Program,
    QuantumArgument,
    QuantumGate,
    QuantumGateModifier,
    QuantumMeasurementAssignment,
    QuantumPhase,
    Qubit,
    QubitDeclaration,
    QuantumGateDefinition,
    QuantumBarrier,
    QuantumMeasurement,
    QuantumReset,
    RangeDefinition,
    RealLiteral,
    ReturnStatement,
    Selection,
    Slice,
    Span,
    SubroutineDefinition,
    Subscript,
    StretchType,
    StringLiteral,
    TimeUnit,
    DurationLiteral,
    UintType,
    UnaryExpression,
    UnaryOperator,
    WhileLoop,
)

_TYPE_NODE_INIT = {"int": IntType, "uint": UintType, "float": FloatType, "angle": AngleType}


def parse(openqasm3_program: str) -> OpenNode:
    lexer = qasm3Lexer(InputStream(openqasm3_program))
    stream = CommonTokenStream(lexer)
    parser = qasm3Parser(stream)

    tree = parser.program()

    return OpenNodeVisitor().visitProgram(tree)


def get_span(node: Union[ParserRuleContext, TerminalNode]) -> Span:
    """Get the span of a node"""
    if isinstance(node, ParserRuleContext):
        return Span(node.start.line, node.start.column, node.stop.line, node.stop.column)
    else:
        return Span(node.symbol.line, node.symbol.start, node.symbol.line, node.symbol.stop)


def add_span(open_node: OpenNode, span: Span) -> OpenNode:
    """Set the span of a node and return the node"""
    open_node.span = span
    return open_node


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


class OpenNodeVisitor(qasm3Visitor):
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
                Qubit(
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
        value = self.visit(ctx.indexIdentifier())
        return AliasStatement(add_span(target, get_span(ctx.Identifier())), value)

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
        qubits = [self.visit(qubit) for qubit in ctx.indexIdentifierList().indexIdentifier()]

        gate = QuantumGate(modifiers=modifiers, name=gate_name, arguments=arguments, qubits=qubits)

        return gate

    @span
    def visitQuantumPhase(self, ctx: qasm3Parser.QuantumPhaseContext):
        modifiers = [self.visit(modifier) for modifier in ctx.quantumGateModifier()]
        argument = self.visit(ctx.expression())
        qubits = []
        if ctx.indexIdentifierList():
            qubits = [self.visit(qubit) for qubit in ctx.indexIdentifierList().indexIdentifier()]

        return QuantumPhase(modifiers, argument, qubits)

    @span
    def visitIndexIdentifier(self, ctx: qasm3Parser.IndexIdentifierContext):
        if ctx.Identifier():
            name = ctx.Identifier().getText()

            if ctx.expressionList():
                expr_list = []
                for expr in ctx.expressionList().expression():
                    expr_list.append(self.visit(expr))
                if len(expr_list) > 1:
                    subscript = Selection(name=name, indices=expr_list)
                else:
                    subscript = Subscript(name=name, index=expr_list[0])

            elif ctx.rangeDefinition():
                subscript = Slice(name=name, range=self.visit(ctx.rangeDefinition()))

            else:
                return add_span(Identifier(name=ctx.Identifier().getText()), get_span(ctx))

        else:
            id0 = self.visit(ctx.indexIdentifier()[0])
            id1 = self.visit(ctx.indexIdentifier()[1])

            return Concatenation(lhs=id0, rhs=id1)

        return subscript

    @span
    def visitQuantumReset(self, ctx: qasm3Parser.QuantumResetContext):
        index_identifier_list = [
            self.visit(id) for id in ctx.indexIdentifierList().indexIdentifier()
        ]
        return QuantumReset(index_identifier_list)

    @span
    def visitQuantumBarrier(self, ctx: qasm3Parser.QuantumBarrierContext):
        index_identifier_list = [
            self.visit(id) for id in ctx.indexIdentifierList().indexIdentifier()
        ]
        return QuantumBarrier(index_identifier_list)

    @span
    def visitQuantumMeasurement(self, ctx: qasm3Parser.QuantumMeasurementContext):
        return QuantumMeasurement(self.visit(ctx.indexIdentifier()))

    @span
    def visitQuantumMeasurementAssignment(
        self, ctx: qasm3Parser.QuantumMeasurementAssignmentContext
    ):
        return QuantumMeasurementAssignment(
            self.visit(ctx.indexIdentifier()), self.visit(ctx.quantumMeasurement())
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
        elif ctx.noDesignatorDeclaration():
            return self.visit(ctx.noDesignatorDeclaration())
        elif ctx.bitDeclaration():
            return self.visit(ctx.bitDeclaration())
        elif ctx.complexDeclaration():
            return self.visit(ctx.complexDeclaration())
        else:
            raise NotImplementedError(f"Not implemented ClassicalDeclaration at {get_span(ctx)}")

    @span
    def visitConstantDeclaration(self, ctx: qasm3Parser.ConstantDeclarationContext):
        return ConstantDeclaration(
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
        if ctx.getText() == "bool":
            return add_span(BoolType(), get_span(ctx))
        elif ctx.timingType().getText() == "duration":
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
            type_designator = self.visit(ctx.designator())
            type_node = _TYPE_NODE_INIT[type_name](type_designator)
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
        elif ctx.Integer():
            return IntegerLiteral(int(ctx.Integer().getText()))
        elif ctx.RealNumber():
            return RealLiteral(float(ctx.RealNumber().getText()))
        elif ctx.booleanLiteral():
            return BooleanLiteral(True if ctx.booleanLiteral().getText() == "true" else False)
        elif ctx.Identifier():
            return Identifier(ctx.Identifier().getText())
        elif ctx.StringLiteral():
            return StringLiteral(ctx.StringLiteral().getText()[1:-1])
        elif ctx.builtInCall():
            return self.visit(ctx.builtInCall())
        elif ctx.externOrSubroutineCall():
            return self.visit(ctx.externOrSubroutineCall())
        elif ctx.timingIdentifier():
            return self.visit(ctx.timingIdentifier())
        elif ctx.LPAREN():
            return self.visit(ctx.expression())
        elif ctx.expressionTerminator():
            return IndexExpression(
                self.visit(ctx.expressionTerminator()), self.visit(ctx.expression())
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
        return UnaryExpression(
            UnaryOperator[ctx.unaryOperator().getText()],
            self.visit(ctx.powerExpression()),
        )

    @span
    def visitBuiltInCall(self, ctx: qasm3Parser.BuiltInCallContext):
        if ctx.builtInMath():
            return FunctionCall(
                self.visit(ctx.builtInMath()),
                [self.visit(expression) for expression in ctx.expressionList().expression()],
            )
        else:
            return Cast(
                self.visit(ctx.castOperator().classicalType()),
                [self.visit(expression) for expression in ctx.expressionList().expression()],
            )

    @span
    def visitBuiltInMath(self, ctx: qasm3Parser.BuiltInMathContext):
        return Identifier(ctx.getText())

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
    def visitCalibrationGrammarDeclaration(
        self, ctx: qasm3Parser.CalibrationGrammarDeclarationContext
    ):
        return CalibrationGrammarDeclaration(
            calibration_grammar=ctx.calibrationGrammar().getText()[1:-1]
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
                add_span(Qubit(id.getText()), get_span(id))
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
        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_designator = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_designator)
            else:
                # To capture potential parser error.
                raise ValueError("Type name {type_name} not found.")

            classcal_type = add_span(
                type_node,
                combine_span(get_span(ctx.singleDesignatorType()), get_span(ctx.designator())),
            )

        elif ctx.noDesignatorType():
            classcal_type = self.visit(ctx.noDesignatorType())

        else:
            classcal_type = add_span(
                BitType(
                    self.visit(ctx.designator()) if ctx.designator() else None,
                ),
                get_span(ctx.getChild(0)),
            )

        identifier = add_span(Identifier(ctx.Identifier().getText()), get_span(ctx.Identifier()))
        return ClassicalArgument(classcal_type, identifier)

    def visitExpressionList(self, ctx: qasm3Parser.ExpressionListContext):
        return [self.visit(expression) for expression in ctx.expression()]

    @span
    def visitClassicalType(self, ctx: qasm3Parser.ClassicalTypeContext):
        # TODO: due to the way classical argument is declared, there some duplication
        # Consider refactor classical argument grammar
        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_designator = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_designator)
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
    def visitNumericType(self, ctx: qasm3Parser.NumericTypeContext):
        # TODO: This method has significant duplication with visitClassicalType
        # Need to refactor the syntax.
        if ctx.singleDesignatorType():
            type_name = ctx.singleDesignatorType().getText()
            if type_name in _TYPE_NODE_INIT:
                type_designator = self.visit(ctx.designator())
                type_node = _TYPE_NODE_INIT[type_name](type_designator)
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
    def visitReturnStatement(self, ctx: qasm3Parser.ReturnStatementContext):
        return ReturnStatement(
            expression=self.visit(ctx.getChild(1)) if ctx.getChildCount() > 1 else None
        )

    @span
    def visitQuantumArgument(self, ctx: qasm3Parser.QuantumArgumentContext):
        return QuantumArgument(
            add_span(
                Qubit(
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

    def visitSetDeclaration(self, ctx: qasm3Parser.SetDeclarationContext):
        if ctx.Identifier():
            return add_span(
                Identifier(name=ctx.Identifier().getText()),
                get_span(ctx),
            )
        elif ctx.rangeDefinition():
            return self.visit(ctx.rangeDefinition())
        else:
            return [self.visit(expression) for expression in ctx.expressionList().expression()]

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
    def visitTimingStatement(self, ctx: qasm3Parser.TimingStatementContext):
        return self.visit(ctx.getChild(0))

    @span
    def visitTimingInstruction(self, ctx: qasm3Parser.TimingInstructionContext):
        return DelayInstruction(
            arguments=[self.visit(expression) for expression in ctx.expressionList().expression()]
            if ctx.expressionList()
            else [],
            duration=self.visit(ctx.designator()),
            qubits=[self.visit(qubit) for qubit in ctx.indexIdentifierList().indexIdentifier()],
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
        if ctx.designator():
            return ClassicalAssignment(
                lvalue=add_span(
                    Subscript(
                        name=ctx.Identifier().getText(),
                        index=self.visit(ctx.designator()),
                    ),
                    combine_span(get_span(ctx.Identifier()), get_span(ctx.designator())),
                ),
                op=AssignmentOperator[ctx.assignmentOperator().getText()],
                rvalue=self.visit(ctx.expression()),
            )
        else:
            return ClassicalAssignment(
                lvalue=add_span(
                    Identifier(name=ctx.Identifier().getText()),
                    get_span(ctx.Identifier()),
                ),
                op=AssignmentOperator[ctx.assignmentOperator().getText()],
                rvalue=self.visit(ctx.expression()),
            )
