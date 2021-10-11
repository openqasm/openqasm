"""
========================================
Abstract Syntax Tree (``openqasm3.ast``)
========================================

.. currentmodule:: openqasm3.ast

The reference abstract syntax tree (AST) for OpenQASM 3 programs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum, auto


__all__ = [
    "AliasStatement",
    "AngleType",
    "AssignmentOperator",
    "BinaryExpression",
    "BinaryOperator",
    "BitType",
    "BoolType",
    "BooleanLiteral",
    "Box",
    "BranchingStatement",
    "BreakStatement",
    "CalibrationDefinition",
    "CalibrationGrammarDeclaration",
    "Cast",
    "ClassicalArgument",
    "ClassicalAssignment",
    "ClassicalDeclaration",
    "ClassicalType",
    "ComplexType",
    "Concatenation",
    "Constant",
    "ConstantDeclaration",
    "ConstantName",
    "ContinueStatement",
    "ControlDirectiveStatement",
    "DelayInstruction",
    "DurationLiteral",
    "DurationOf",
    "DurationType",
    "EndStatement",
    "Expression",
    "ExpressionStatement",
    "ExternDeclaration",
    "FloatType",
    "ForInLoop",
    "FunctionCall",
    "GateModifierName",
    "IODeclaration",
    "IOKeyword",
    "Identifier",
    "Include",
    "IndexExpression",
    "IntType",
    "IntegerLiteral",
    "Program",
    "QASMNode",
    "QuantumArgument",
    "QuantumBarrier",
    "QuantumForInLoop",
    "QuantumGate",
    "QuantumGateDefinition",
    "QuantumGateModifier",
    "QuantumInstruction",
    "QuantumMeasurement",
    "QuantumMeasurementAssignment",
    "QuantumPhase",
    "QuantumReset",
    "QuantumStatement",
    "QuantumWhileLoop",
    "QubitDeclaration",
    "RangeDefinition",
    "RealLiteral",
    "ReturnStatement",
    "Span",
    "Statement",
    "StretchType",
    "StringLiteral",
    "SubroutineDefinition",
    "TimeUnit",
    "TimingStatement",
    "UintType",
    "UnaryExpression",
    "UnaryOperator",
    "WhileLoop",
]


@dataclass
class Span:
    """
    Start and end line/column in the source file
    We use the Antlr convention. The starting line number is 1 and starting column number is 0.
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int


@dataclass
class QASMNode:
    """Base class for all OpenQASM 3 nodes"""

    span: Optional[Span] = field(init=False, default=None, compare=False)
    """
    The span(location) of the node in the source code.
    Because not all the nodes are generated from source, the span is optional.
    To make it easier to write unit test, we exclude span from the generated __eq__().
    """


@dataclass
class Program(QASMNode):
    """
    An entire OpenQASM 3 program represented by a list of top level statements
    """

    statements: List[Statement]
    version: str = field(init=False, default="")
    includes: List[Include] = field(init=False, default_factory=list)
    io_variables: List[IODeclaration] = field(init=False, default_factory=list)


@dataclass
class Include(QASMNode):
    """
    An include statement
    """

    filename: str


class Statement(QASMNode):
    """A statement: anything that can appear on its own line"""


@dataclass
class ExpressionStatement(Statement):
    """A statement that contains a single expression"""

    expression: Expression


@dataclass
class QubitDeclaration(Statement):
    """
    Global qubit declaration

    Example::

        qubit q;
        qubit[4] q;

        q // <- qubit
        [4] // <- designator

    """

    qubit: Identifier
    size: Optional[Expression]


@dataclass
class QuantumGateDefinition(Statement):
    """
    Define a new quantum gate

    Example::

        gate cx c, t {
            ctrl @ unitary(pi, 0, pi) c, t;
        }

    """

    name: Identifier
    arguments: List[ClassicalArgument]
    qubits: List[Identifier]
    body: List[QuantumStatement]


class QuantumStatement(Statement):
    """Statements that may appear inside a gate declaration"""


@dataclass
class QuantumForInLoop(Statement):
    """For In loops that contain only quantum statements."""

    loop_variable: Identifier
    set_declaration: Union[RangeDefinition, List[Expression], Identifier]
    block: List[QuantumStatement]


@dataclass
class QuantumWhileLoop(Statement):
    """While loops that contain only quantum statements."""

    while_condition: Expression
    block: List[QuantumStatement]


@dataclass
class ExternDeclaration(Statement):
    """
    A extern declaration

    Example::

        extern get_pauli(int[prec]) -> bit[2 * n];

        get_pauli  // <- name
        int[prec]  // <- classical type
        bit[2 * n] // <- return type

    """

    name: Identifier
    classical_types: List[ClassicalType]
    return_type: Optional[ClassicalType]


class Expression(QASMNode):
    """An expression: anything that returns a value"""


@dataclass
class Identifier(Expression):
    """
    An identifier

    Example::

        q1

    """

    name: str


UnaryOperator = Enum("UnaryOperator", "~ ! -")


@dataclass
class UnaryExpression(Expression):
    """
    A unary expression

    Example::

        ~b
        !bool
        -i

    """

    op: UnaryOperator
    expression: Expression


BinaryOperator = Enum("BinaryOperator", "> < >= <= == != && || | ^ & << >> + - * / % **")


@dataclass
class BinaryExpression(Expression):
    """
    A binary expression

    Example::

        q1 || q2

    """

    op: BinaryOperator
    lhs: Expression
    rhs: Expression


class ConstantName(Enum):
    """
    Known constant names
    """

    pi = auto()
    tau = auto()
    euler = auto()


@dataclass
class Constant(Expression):
    """
    A constant expression

    Example::

        π
        𝜏
        ℇ
    """

    name: ConstantName


@dataclass
class IntegerLiteral(Expression):
    """
    An integer literal

    Example::

        1

    """

    value: int


@dataclass
class RealLiteral(Expression):
    """
    An real number literal

    Example::

        1.1

    """

    value: float


@dataclass
class BooleanLiteral(Expression):
    """
    A boolean expression

    Example::

        true
        false

    """

    value: bool


@dataclass
class StringLiteral(Expression):
    """
    A string literal expression

    Example::

        'Hadamard gate'

    """

    value: str


class TimeUnit(Enum):
    dt = auto()
    ns = auto()
    us = auto()
    ms = auto()
    s = auto()


@dataclass
class DurationLiteral(Expression):
    """
    A duration literal

    Example::

        1.0ns

    """

    value: float
    unit: TimeUnit


@dataclass
class ArrayLiteral(Expression):
    """Array literal, used to initialise declared arrays.

    For example::

        array[uint[8], 2] row = {1, 2};
        array[uint[8], 2, 2] my_array = {{1, 2}, {3, 4}};
        array[uint[8], 2, 2] my_array = {row, row};
    """

    values: List[Expression]


@dataclass
class FunctionCall(Expression):
    """
    A function call expression

    Example::

        foo(1)

        foo // <- name

    """

    name: Identifier
    arguments: List[Expression]


@dataclass
class Cast(Expression):
    """
    A cast call expression

    Example::

        counts += int[1](b);

    """

    type: ClassicalType
    arguments: List[Expression]


@dataclass
class DiscreteSet(QASMNode):
    """
    A set of discrete values.  This can be used for the values in a ``for``
    loop, or to index certain values out of a register::

        for i in {1, 2, 3} {}
        let alias = qubits[{2, 3, 4}];
    """

    values: List[Expression]


@dataclass
class RangeDefinition(QASMNode):
    """
    Range definition.

    Example::

        1:2
        1:1:10
        :
    """

    start: Optional[Expression]
    end: Optional[Expression]
    step: Optional[Expression]


IndexElement = Union[DiscreteSet, List[Union[Expression, RangeDefinition]]]


@dataclass
class IndexExpression(Expression):
    """
    An index expression.

    Example::

        q[1]
    """

    collection: Expression
    index: IndexElement


@dataclass
class IndexedIdentifier(QASMNode):
    """An indentifier with index operators, such that it can be used as an
    lvalue.  The list of indices is subsequent index brackets, so in::

        a[{1, 2, 3}][0:1, 0:1]

    the list of indices will have two elements.  The first will be a
    :class:`.DiscreteSet`, and the second will be a list of two
    :class:`.RangeDefinition`\\ s.
    """

    name: Identifier
    indices: List[IndexElement]


@dataclass
class Concatenation(Expression):
    """
    Concatenation of two registers, for example::

        a ++ b
        a[2:3] ++ a[0:1]
    """

    lhs: Expression
    rhs: Expression


class QuantumInstruction(QuantumStatement):
    """
    Baseclass for quantum instructions.
    """


@dataclass
class QuantumGate(QuantumInstruction):
    """
    Invoking a quantum gate

    Example::
        cx 0, 1;

        or

        ctrl @ p(λ) a, b;

        ctrl @ // <- quantumGateModifier
        p // <- quantumGateName
        λ // <- argument
        a, b // <- qubit
    """

    modifiers: List[QuantumGateModifier]
    name: Identifier
    arguments: List[Expression]
    qubits: List[Expression]


class GateModifierName(Enum):
    inv = auto()
    pow = auto()
    ctrl = auto()
    negctrl = auto()


@dataclass
class QuantumGateModifier(QASMNode):
    """
    A quantum gate modifier

    Attributes:
        modifier: 'inv', 'pow', or 'ctrl'
        expression: only pow modifier has expression.

    Example::

        inv @
        pow(1/2)
        ctrl
    """

    modifier: GateModifierName
    argument: Optional[Expression]


@dataclass
class QuantumPhase(QuantumInstruction):
    """
    A quantum phase instruction

    Example::

        ctrl @ gphase(λ) a;

        ctrl @ // <- quantumGateModifier
        λ // <- argument
        a // <- qubit

    """

    quantum_gate_modifiers: List[QuantumGateModifier]
    argument: Expression
    qubits: List[Union[IndexedIdentifier, Identifier]]


@dataclass
class QuantumMeasurement(QuantumInstruction):
    """
    A quantum measurement instruction

    Example::

        measure q;
    """

    qubit: Union[IndexedIdentifier, Identifier]


@dataclass
class QuantumReset(QuantumInstruction):
    """
    A reset instruction.

    Example::

        reset q;
    """

    qubits: Union[IndexedIdentifier, Identifier]


@dataclass
class QuantumBarrier(QuantumInstruction):
    """
    A quantum barrier instruction

    Example::

        barrier q;
    """

    qubits: List[Union[IndexedIdentifier, Identifier]]


@dataclass
class QuantumMeasurementAssignment(Statement):
    """
    A quantum measurement assignment statement

    Example::

        c = measure q;
    """

    target: Union[IndexedIdentifier, Identifier]
    measure_instruction: QuantumMeasurement


class AccessControl(Enum):
    """Access modifier for classical arguments."""

    CONST = auto()
    MUTABLE = auto()


@dataclass
class ClassicalArgument(QASMNode):
    """
    Classical argument for a gate or subroutine declaration
    """

    type: ClassicalType
    name: Identifier
    access: Optional[AccessControl] = None


@dataclass
class ClassicalDeclaration(Statement):
    """
    Classical variable declaration

    Example::

        bit c;
    """

    type: ClassicalType
    identifier: Identifier
    init_expression: Optional[Expression]


class IOKeyword(Enum):
    output = auto()
    input = auto()


@dataclass
class IODeclaration(ClassicalDeclaration):
    """
    Input/output variable declaration

    Exampe::

        input angle[16] theta;
        output bit select;
    """

    io_identifier: IOKeyword


@dataclass
class ConstantDeclaration(Statement):
    """
    Constant declaration

    Example::

        const int[16] n = 10;
    """

    type: ClassicalType
    identifier: Identifier
    init_expression: Expression


class ClassicalType(QASMNode):
    """
    Base class for classical type
    """


@dataclass
class IntType(ClassicalType):
    """
    Node representing a classical ``int`` (signed integer) type, with an
    optional precision.

    Example:

        int[8]
        int[16]
    """

    size: Optional[Expression]


@dataclass
class UintType(ClassicalType):
    """
    Node representing a classical ``uint`` (unsigned integer) type, with an
    optional precision.

    Example:

        uint[8]
        uint[16]
    """

    size: Optional[Expression]


@dataclass
class FloatType(ClassicalType):
    """
    Node representing the classical ``float`` type, with the particular IEEE-754
    floating-point size optionally specified.

    Example:

        float[16]
        float[64]
    """

    size: Optional[Expression]


@dataclass
class ComplexType(ClassicalType):
    """
    Complex Type. Its real and imaginary parts are based on other classical types.

    Example::

        complex[int[32]]
        complex[float[32]]
    """

    base_type: Union[IntType, UintType, FloatType, AngleType]


@dataclass
class AngleType(ClassicalType):
    """
    Node representing the classical ``angle`` type, with an optional precision.

    Example::

        angle[8]
        angle[16]
    """

    size: Optional[Expression]


@dataclass
class BitType(ClassicalType):
    """
    Node representing the classical ``bit`` type, with an optional size.

    Example::

        bit[8]
        creg[8]
    """

    size: Optional[Expression]


class BoolType(ClassicalType):
    """
    Leaf node representing the Boolean classical type.
    """


@dataclass
class ArrayType(ClassicalType):
    """Type of arrays that include allocation of the storage.

    This is generally any array declared as a standard statement, but not
    arrays declared by being arguments to subroutines.
    """

    base_type: Union[IntType, UintType, FloatType, AngleType, BitType, BoolType, ComplexType]
    dimensions: List[Expression]


@dataclass
class ArrayReferenceType(ClassicalType):
    """Type of arrays that are a reference to an array with allocated storage.

    This is generally any array declared as a subroutine argument.  The
    dimensions can be either a list of expressions (one for each dimension), or
    a single expression, which is the number of dimensions.

    For example::

        // `a` will have dimensions `[IntegerLiteral(2)]` (with a list), because
        // it is a 1D array, with a length of 2.
        def f(const array[uint[8], 2] a) {}
        // `b` will have dimension `IntegerLiteral(3)` (no list), because it is
        // a 3D array, but we don't know the lengths of its dimensions.
        def f(const array[uint[8], #dim=3] b) {}
    """

    base_type: Union[IntType, UintType, FloatType, AngleType, BitType, BoolType, ComplexType]
    dimensions: Union[Expression, List[Expression]]


class DurationType(ClassicalType):
    """
    Leaf node representing the ``duration`` type.
    """


class StretchType(ClassicalType):
    """
    Leaf node representing the ``stretch`` type.
    """


@dataclass
class CalibrationGrammarDeclaration(Statement):
    """
    Calibration grammar declaration

    Example::

        defcalgrammar "openpulse";
    """

    calibration_grammar: str


@dataclass
class CalibrationDefinition(Statement):
    """
    Calibration definition

    Example::

        defcal rz(angle[20] theta) $q {
            shift_phase drive($q), -theta;
        }
    """

    name: Identifier
    arguments: List[ClassicalArgument]
    qubits: List[Identifier]
    return_type: Optional[ClassicalType]
    body: str


@dataclass
class SubroutineDefinition(Statement):
    """
    Subroutine definition

    Example::

        def measure(qubit q) -> bit {
            s q;
            h q;
            return measure q;
        }
    """

    name: Identifier
    arguments: List[Union[ClassicalArgument, QuantumArgument]]
    return_type: Optional[ClassicalType]
    body: List[Statement]


@dataclass
class QuantumArgument(QASMNode):
    """
    Quantum argument in subroutine definition

    Example::

        qubit q
        qubit[4] q
    """

    qubit: Identifier
    size: Optional[Expression]


@dataclass
class ReturnStatement(Statement):
    """
    Classical or quantum return statement

    Example::

        return measure q;

        return a + b

    """

    expression: Optional[Union[Expression, QuantumMeasurement]]


class ControlDirectiveStatement(Statement):
    """
    Base class for control directive statements
    """


class BreakStatement(ControlDirectiveStatement):
    """
    Break statement

    Example::

        break;
    """


class ContinueStatement(ControlDirectiveStatement):
    """
    Continue statement

    Example::

        continue;
    """


class EndStatement(ControlDirectiveStatement):
    """
    End statement

    Example::

        end;
    """


@dataclass
class BranchingStatement(Statement):
    """
    Branch (``if``) statement

    Example::

        if (temp == 1) {
            ry(-pi / 2) scratch[0];
        } else continue;
    """

    condition: Expression
    if_block: List[Statement]
    else_block: List[Statement]


@dataclass
class WhileLoop(Statement):
    """
    While loop

    Example::

        while(~success) {
            reset magic;
            ry(pi / 4) magic;
            success = distill(magic, scratch);
        }
    """

    while_condition: Expression
    block: List[Statement]


@dataclass
class ForInLoop(Statement):
    """
    For in loop

    Example::

        for i in [0: 2] {
            majority a[i], b[i + 1], a[i + 1];
        }
    """

    loop_variable: Identifier
    set_declaration: Union[RangeDefinition, DiscreteSet, Identifier]
    block: List[Statement]


class TimingStatement(QuantumStatement):
    """
    Base class for timing statement
    """


@dataclass
class DelayInstruction(TimingStatement):
    """
    Delay instruction

    Example::

        delay[start_stretch] $0;
    """

    arguments: List[Expression]
    duration: Expression
    qubits: List[Expression]


@dataclass
class Box(TimingStatement):
    """
    Timing box

    Example::

        box [maxdur] {
            delay[start_stretch] $0;
            x $0;
        }
    """

    duration: Optional[Expression]
    body: List[QuantumStatement]


@dataclass
class DurationOf(QASMNode):
    """
    Duration Of

    Example::

        durationof({x $0;})
    """

    target: Union[Identifier, List[QuantumStatement]]


@dataclass
class AliasStatement(Statement):
    """
    Alias statement

    Example::

        let a = qubits[0];

    """

    target: Identifier
    value: Union[Identifier, Concatenation]


AssignmentOperator = Enum("AssignmentOperator", "= += -= *= /= &= |= ~= ^= <<= >>= %= **=")


@dataclass
class ClassicalAssignment(Statement):
    """
    Classical assignment

    Example::

        a[0] = 1;
    """

    lvalue: Union[Identifier, IndexedIdentifier]
    op: AssignmentOperator
    rvalue: Expression


@dataclass
class Pragma(Statement):
    """
    Pragma
    Example::

        #pragma {verbatim;}
    """

    statements: List[Statement]
