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

try:
    from antlr4 import CommonTokenStream, InputStream
    from antlr4.tree.Tree import TerminalNode
except ImportError as exc:
    raise ImportError(
        "Parsing is not available unless the [parser] extra is installed,"
        " such as by 'pip install openqasm3[parser]'."
    ) from exc

from openqasm3.parser import get_span, add_span, span, QASMNodeVisitor

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


class OpenPulseNodeVisitor(openpulseParserVisitor):
    # Try to reuse some methods from QASMNodeVisitor
    # The following block can be generated/refreshed with:
    # from openqasm3.parser import QASMNodeVisitor
    # import re
    # p = p = re.compile("_?visit.+")
    # for m in dir(QASMNodeVisitor):
    #  if p.match(m) and m != "visitCalibrationDefinition":
    #    print(f"{m} = QASMNodeVisitor.{m}")
    _visitBinaryExpression = QASMNodeVisitor._visitBinaryExpression
    visitAdditiveExpression = QASMNodeVisitor.visitAdditiveExpression
    visitAliasInitializer = QASMNodeVisitor.visitAliasInitializer
    visitAliasStatement = QASMNodeVisitor.visitAliasStatement
    visitAnyTypeArgument = QASMNodeVisitor.visitAnyTypeArgument
    visitAnyTypeArgumentList = QASMNodeVisitor.visitAnyTypeArgumentList
    visitArrayDeclaration = QASMNodeVisitor.visitArrayDeclaration
    visitArrayInitializer = QASMNodeVisitor.visitArrayInitializer
    visitArrayReferenceType = QASMNodeVisitor.visitArrayReferenceType
    visitArrayReferenceTypeDimensionSpecifier = (
        QASMNodeVisitor.visitArrayReferenceTypeDimensionSpecifier
    )
    visitArrayType = QASMNodeVisitor.visitArrayType
    visitAssignmentOperator = QASMNodeVisitor.visitAssignmentOperator
    visitAssignmentStatement = QASMNodeVisitor.visitAssignmentStatement
    visitBitAndExpression = QASMNodeVisitor.visitBitAndExpression
    visitBitDeclaration = QASMNodeVisitor.visitBitDeclaration
    visitBitOrExpression = QASMNodeVisitor.visitBitOrExpression
    visitBitShiftExpression = QASMNodeVisitor.visitBitShiftExpression
    visitBitType = QASMNodeVisitor.visitBitType
    visitBranchingStatement = QASMNodeVisitor.visitBranchingStatement
    visitBuiltInCall = QASMNodeVisitor.visitBuiltInCall
    visitCalibration = QASMNodeVisitor.visitCalibration
    visitCalibrationArgumentList = QASMNodeVisitor.visitCalibrationArgumentList
    visitCalibrationGrammarDeclaration = QASMNodeVisitor.visitCalibrationGrammarDeclaration
    visitCastOperator = QASMNodeVisitor.visitCastOperator
    visitChildren = QASMNodeVisitor.visitChildren
    visitClassicalArgument = QASMNodeVisitor.visitClassicalArgument
    visitClassicalArgumentList = QASMNodeVisitor.visitClassicalArgumentList
    visitClassicalAssignment = QASMNodeVisitor.visitClassicalAssignment
    visitClassicalDeclaration = QASMNodeVisitor.visitClassicalDeclaration
    visitClassicalDeclarationStatement = QASMNodeVisitor.visitClassicalDeclarationStatement
    visitClassicalType = QASMNodeVisitor.visitClassicalType
    visitClassicalTypeList = QASMNodeVisitor.visitClassicalTypeList
    visitComparisonExpression = QASMNodeVisitor.visitComparisonExpression
    visitComplexDeclaration = QASMNodeVisitor.visitComplexDeclaration
    visitConstantDeclaration = QASMNodeVisitor.visitConstantDeclaration
    visitControlDirective = QASMNodeVisitor.visitControlDirective
    visitCtrlModifier = QASMNodeVisitor.visitCtrlModifier
    visitDesignator = QASMNodeVisitor.visitDesignator
    visitDiscreteSet = QASMNodeVisitor.visitDiscreteSet
    visitEndStatement = QASMNodeVisitor.visitEndStatement
    visitEqualityExpression = QASMNodeVisitor.visitEqualityExpression
    visitEqualsExpression = QASMNodeVisitor.visitEqualsExpression
    visitErrorNode = QASMNodeVisitor.visitErrorNode
    visitExpression = QASMNodeVisitor.visitExpression
    visitExpressionList = QASMNodeVisitor.visitExpressionList
    visitExpressionStatement = QASMNodeVisitor.visitExpressionStatement
    visitExpressionTerminator = QASMNodeVisitor.visitExpressionTerminator
    visitExternDeclaration = QASMNodeVisitor.visitExternDeclaration
    visitExternOrSubroutineCall = QASMNodeVisitor.visitExternOrSubroutineCall
    visitGlobalStatement = QASMNodeVisitor.visitGlobalStatement
    visitHeader = QASMNodeVisitor.visitHeader
    visitIdentifierList = QASMNodeVisitor.visitIdentifierList
    visitInclude = QASMNodeVisitor.visitInclude
    visitIndexExpression = QASMNodeVisitor.visitIndexExpression
    visitIndexOperator = QASMNodeVisitor.visitIndexOperator
    visitIndexedIdentifier = QASMNodeVisitor.visitIndexedIdentifier
    visitIo = QASMNodeVisitor.visitIo
    visitIoIdentifier = QASMNodeVisitor.visitIoIdentifier
    visitLogicalAndExpression = QASMNodeVisitor.visitLogicalAndExpression
    visitLoopSignature = QASMNodeVisitor.visitLoopSignature
    visitLoopStatement = QASMNodeVisitor.visitLoopStatement
    visitMultiplicativeExpression = QASMNodeVisitor.visitMultiplicativeExpression
    visitNoDesignatorDeclaration = QASMNodeVisitor.visitNoDesignatorDeclaration
    visitNoDesignatorType = QASMNodeVisitor.visitNoDesignatorType
    visitNonArrayType = QASMNodeVisitor.visitNonArrayType
    visitNumericType = QASMNodeVisitor.visitNumericType
    visitPowModifier = QASMNodeVisitor.visitPowModifier
    visitPowerExpression = QASMNodeVisitor.visitPowerExpression
    visitPragma = QASMNodeVisitor.visitPragma
    visitProgram = QASMNodeVisitor.visitProgram
    visitProgramBlock = QASMNodeVisitor.visitProgramBlock
    visitQuantumArgument = QASMNodeVisitor.visitQuantumArgument
    visitQuantumBarrier = QASMNodeVisitor.visitQuantumBarrier
    visitQuantumBlock = QASMNodeVisitor.visitQuantumBlock
    visitQuantumDeclaration = QASMNodeVisitor.visitQuantumDeclaration
    visitQuantumDeclarationStatement = QASMNodeVisitor.visitQuantumDeclarationStatement
    visitQuantumGateCall = QASMNodeVisitor.visitQuantumGateCall
    visitQuantumGateDefinition = QASMNodeVisitor.visitQuantumGateDefinition
    visitQuantumGateModifier = QASMNodeVisitor.visitQuantumGateModifier
    visitQuantumGateName = QASMNodeVisitor.visitQuantumGateName
    visitQuantumGateSignature = QASMNodeVisitor.visitQuantumGateSignature
    visitQuantumInstruction = QASMNodeVisitor.visitQuantumInstruction
    visitQuantumLoop = QASMNodeVisitor.visitQuantumLoop
    visitQuantumLoopBlock = QASMNodeVisitor.visitQuantumLoopBlock
    visitQuantumMeasurement = QASMNodeVisitor.visitQuantumMeasurement
    visitQuantumMeasurementAssignment = QASMNodeVisitor.visitQuantumMeasurementAssignment
    visitQuantumPhase = QASMNodeVisitor.visitQuantumPhase
    visitQuantumReset = QASMNodeVisitor.visitQuantumReset
    visitQuantumStatement = QASMNodeVisitor.visitQuantumStatement
    visitRangeDefinition = QASMNodeVisitor.visitRangeDefinition
    visitReturnSignature = QASMNodeVisitor.visitReturnSignature
    visitReturnStatement = QASMNodeVisitor.visitReturnStatement
    visitSetDeclaration = QASMNodeVisitor.visitSetDeclaration
    visitSingleDesignatorDeclaration = QASMNodeVisitor.visitSingleDesignatorDeclaration
    visitSingleDesignatorType = QASMNodeVisitor.visitSingleDesignatorType
    visitStatement = QASMNodeVisitor.visitStatement
    visitSubroutineBlock = QASMNodeVisitor.visitSubroutineBlock
    visitSubroutineDefinition = QASMNodeVisitor.visitSubroutineDefinition
    visitTerminal = QASMNodeVisitor.visitTerminal
    visitTimingBox = QASMNodeVisitor.visitTimingBox
    visitTimingIdentifier = QASMNodeVisitor.visitTimingIdentifier
    visitTimingInstruction = QASMNodeVisitor.visitTimingInstruction
    visitTimingStatement = QASMNodeVisitor.visitTimingStatement
    visitUnaryExpression = QASMNodeVisitor.visitUnaryExpression
    visitUnaryOperator = QASMNodeVisitor.visitUnaryOperator
    visitVersion = QASMNodeVisitor.visitVersion
    visitXOrExpression = QASMNodeVisitor.visitXOrExpression

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
