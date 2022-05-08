"""

========================================
Abstract Syntax Tree (``openpulse.ast``)
========================================

.. currentmodule:: openpulse.ast

The reference abstract syntax tree (AST) for OpenPulse programs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

# Re-export the existing AST classes from openqasm3
# pylint: disable=unused-import
from openqasm3.ast import (
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
    BitstringLiteral,
    BoolType,
    BooleanLiteral,
    Box,
    BranchingStatement,
    BreakStatement,
    CalibrationGrammarDeclaration,
    Cast,
    ClassicalArgument,
    ClassicalAssignment,
    ClassicalDeclaration,
    ClassicalType,
    ComplexType,
    Concatenation,
    Constant,
    ConstantDeclaration,
    ConstantName,
    ContinueStatement,
    ControlDirectiveStatement,
    DelayInstruction,
    DiscreteSet,
    DurationLiteral,
    DurationOf,
    DurationType,
    EndStatement,
    Expression,
    ExpressionStatement,
    ExternDeclaration,
    FloatLiteral,
    FloatType,
    ForInLoop,
    FunctionCall,
    GateModifierName,
    IODeclaration,
    IOKeyword,
    Identifier,
    Include,
    IndexElement,
    IndexExpression,
    IndexedIdentifier,
    IntType,
    IntegerLiteral,
    Pragma,
    Program,
    QASMNode,
    QuantumArgument,
    QuantumBarrier,
    QuantumForInLoop,
    QuantumGate,
    QuantumGateDefinition,
    QuantumGateModifier,
    QuantumInstruction,
    QuantumMeasurement,
    QuantumMeasurementAssignment,
    QuantumPhase,
    QuantumReset,
    QuantumStatement,
    QuantumWhileLoop,
    QubitDeclaration,
    RangeDefinition,
    ReturnStatement,
    Span,
    Statement,
    StretchType,
    StringLiteral,
    SubroutineDefinition,
    TimeUnit,
    TimingStatement,
    UintType,
    UnaryExpression,
    UnaryOperator,
    Union,
    WhileLoop,
)


# From Pulse grammar
class PulseTypeName(Enum):
    waveform = auto()
    port = auto()
    frame = auto()


@dataclass
class PulseType(ClassicalType):
    """
    Pulse type

    Example::
        waveform
        port
        frame
    """

    type: PulseTypeName


@dataclass
class CalibrationBlock(Statement):
    """
    Cal block

    Example::

        cal {

            extern drag(complex[size], duration, duration, float[size]) -> waveform;
            extern gaussian_square(complex[size], duration, duration, duration) -> waveform;

            port q0 = getport("q", $0);
            port q1 = getport("q", $1);

            frame q0_frame = newframe(q0_freq, 0);
            frame q1_frame = newframe(q1_freq, 0);
        }
    """

    body: List[Statement]


# Override the class from openqasm3
@dataclass
class CalibrationDefinition(Statement):
    """
    Calibration definition

    Example::

        defcal rz(angle[20] theta) $q {
            shift_phase(drive($q), -theta);
        }
    """

    name: Identifier
    arguments: List[ClassicalArgument]
    qubits: List[Identifier]
    return_type: Optional[ClassicalType]
    body: List[Statement]
