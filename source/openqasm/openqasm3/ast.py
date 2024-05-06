"""
========================================
Abstract Syntax Tree (``openqasm3.ast``)
========================================

.. currentmodule:: openqasm3.ast

The reference abstract syntax tree (AST) for OpenQASM 3 programs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple
from enum import Enum

__all__ = [
    "AccessControl",
    "AliasStatement",
    "AngleType",
    "Annotation",
    "ArrayLiteral",
    "ArrayReferenceType",
    "ArrayType",
    "AssignmentOperator",
    "BinaryExpression",
    "BinaryOperator",
    "BitType",
    "BitstringLiteral",
    "BoolType",
    "BooleanLiteral",
    "Box",
    "BranchingStatement",
    "BreakStatement",
    "CalibrationDefinition",
    "CalibrationGrammarDeclaration",
    "CalibrationStatement",
    "Cast",
    "ClassicalArgument",
    "ClassicalAssignment",
    "ClassicalDeclaration",
    "ClassicalType",
    "ComplexType",
    "Concatenation",
    "ConstantDeclaration",
    "ContinueStatement",
    "DelayInstruction",
    "DiscreteSet",
    "DurationLiteral",
    "DurationOf",
    "DurationType",
    "EndStatement",
    "Expression",
    "ExpressionStatement",
    "ExternArgument",
    "ExternDeclaration",
    "FloatLiteral",
    "FloatType",
    "ForInLoop",
    "FunctionCall",
    "GateModifierName",
    "IODeclaration",
    "IOKeyword",
    "Identifier",
    "ImaginaryLiteral",
    "Include",
    "IndexExpression",
    "IndexedIdentifier",
    "IntType",
    "IntegerLiteral",
    "Pragma",
    "Program",
    "QASMNode",
    "QuantumArgument",
    "QuantumBarrier",
    "QuantumGate",
    "QuantumGateDefinition",
    "QuantumGateModifier",
    "QuantumMeasurement",
    "QuantumMeasurementStatement",
    "QuantumPhase",
    "QuantumReset",
    "QuantumStatement",
    "QubitDeclaration",
    "RangeDefinition",
    "ReturnStatement",
    "SizeOf",
    "Span",
    "Statement",
    "SwitchStatement",
    "CompoundStatement",
    "StretchType",
    "SubroutineDefinition",
    "TimeUnit",
    "UintType",
    "UnaryExpression",
    "UnaryOperator",
    "WhileLoop",
]

AccessControl = Enum("AccessControl", "readonly mutable")
AssignmentOperator = Enum("AssignmentOperator", "= += -= *= /= &= |= ~= ^= <<= >>= %= **=")
BinaryOperator = Enum("BinaryOperator", "> < >= <= == != && || | ^ & << >> + - * / % **")
GateModifierName = Enum("GateModifier", "inv pow ctrl negctrl")
IOKeyword = Enum("IOKeyword", "input output")
TimeUnit = Enum("TimeUnit", "dt ns us ms s")
UnaryOperator = Enum("UnaryOperator", "~ ! -")


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
    version: Optional[str] = None


@dataclass
class Annotation(QASMNode):
    """An annotation applied to a statement."""

    keyword: str
    command: Optional[str] = None


@dataclass
class Statement(QASMNode):
    """A statement: anything that can appear on its own line"""

    annotations: List[Annotation] = field(init=False, default_factory=list)


@dataclass
class CompoundStatement(Statement):
    """A sequence of statements enclosed within an anonymous scope block"""

    statements: List[Statement]


@dataclass
class Include(Statement):
    """
    An include statement
    """

    filename: str


@dataclass
class ExpressionStatement(Statement):
    """A statement that contains a single expression"""

    expression: Expression


# Note that QubitDeclaration is not a valid QuantumStatement, because qubits
# can only be declared in global scopes, not in gates.
@dataclass
class QubitDeclaration(Statement):
    """
    Global qubit declaration

    Example::

        qubit q;
        qubit[4] q;

        q // <- qubit
        4 // <- size

    """

    qubit: Identifier
    size: Optional[Expression] = None


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
    arguments: List[Identifier]
    qubits: List[Identifier]
    body: List[QuantumStatement]


class QuantumStatement(Statement):
    """Statements that may appear inside a gate declaration"""


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
    arguments: List[ExternArgument]
    return_type: Optional[ClassicalType] = None


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


@dataclass
class IntegerLiteral(Expression):
    """
    An integer literal

    Example::

        1

    """

    value: int


@dataclass
class FloatLiteral(Expression):
    """
    An real number literal

    Example::

        1.1

    """

    value: float


@dataclass
class ImaginaryLiteral(Expression):
    """
    An real number literal

    Example::

        1.1im

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
class BitstringLiteral(Expression):
    """A literal bitstring value.  The ``value`` is the numerical value of the
    bitstring, and the ``width`` is the number of digits given."""

    value: int
    width: int


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
    argument: Expression


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


@dataclass
class QuantumGate(QuantumStatement):
    """
    Invoking a quantum gate

    Example::
        cx[dur] 0, 1;

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
    qubits: List[Union[IndexedIdentifier, Identifier]]
    duration: Optional[Expression] = None


@dataclass
class QuantumGateModifier(QASMNode):
    """
    A quantum gate modifier

    Attributes:
        modifier: 'inv', 'pow', or 'ctrl'
        expression: only pow modifier has expression.

    Example::

        inv @
        pow(1./2.)
        ctrl
    """

    modifier: GateModifierName
    argument: Optional[Expression] = None


@dataclass
class QuantumPhase(QuantumStatement):
    """
    A quantum phase instruction

    Example::

        ctrl @ gphase(λ) a;

        ctrl @ // <- quantumGateModifier
        λ // <- argument
        a // <- qubit

    """

    modifiers: List[QuantumGateModifier]
    argument: Expression
    qubits: List[Union[IndexedIdentifier, Identifier]]


# Not a full expression because it can only be used in limited contexts.
@dataclass
class QuantumMeasurement(QASMNode):
    """
    A quantum measurement instruction

    Example::

        measure q;
    """

    qubit: Union[IndexedIdentifier, Identifier]


# Note that this is not a QuantumStatement because it involves access to
# classical bits.
@dataclass
class QuantumMeasurementStatement(Statement):
    """Stand-alone statement of a quantum measurement, potentially assigning the
    result to a classical variable.  This is not the only statement that
    `measure` can appear in (it can also be in classical declaration statements
    and returns)."""

    measure: QuantumMeasurement
    target: Optional[Union[IndexedIdentifier, Identifier]]


@dataclass
class QuantumBarrier(QuantumStatement):
    """
    A quantum barrier instruction

    Example::

        barrier q;
    """

    qubits: List[Expression]


@dataclass
class QuantumReset(QuantumStatement):
    """
    A reset instruction.

    Example::

        reset q;
    """

    qubits: Union[IndexedIdentifier, Identifier]


@dataclass
class ClassicalArgument(QASMNode):
    """
    Classical argument for a gate or subroutine declaration
    """

    type: ClassicalType
    name: Identifier
    access: Optional[AccessControl] = None


@dataclass
class ExternArgument(QASMNode):
    """Classical argument for an extern declaration."""

    type: ClassicalType
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
    init_expression: Optional[Union[Expression, QuantumMeasurement]] = None


@dataclass
class IODeclaration(Statement):
    """
    Input/output variable declaration

    Exampe::

        input angle[16] theta;
        output bit select;
    """

    io_identifier: IOKeyword
    type: ClassicalType
    identifier: Identifier


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

    size: Optional[Expression] = None


@dataclass
class UintType(ClassicalType):
    """
    Node representing a classical ``uint`` (unsigned integer) type, with an
    optional precision.

    Example:

        uint[8]
        uint[16]
    """

    size: Optional[Expression] = None


@dataclass
class FloatType(ClassicalType):
    """
    Node representing the classical ``float`` type, with the particular IEEE-754
    floating-point size optionally specified.

    Example:

        float[16]
        float[64]
    """

    size: Optional[Expression] = None


@dataclass
class ComplexType(ClassicalType):
    """
    Complex ClassicalType. Its real and imaginary parts are based on other classical types.

    Example::

        complex[float]
        complex[float[32]]
    """

    base_type: Optional[FloatType]


@dataclass
class AngleType(ClassicalType):
    """
    Node representing the classical ``angle`` type, with an optional precision.

    Example::

        angle[8]
        angle[16]
    """

    size: Optional[Expression] = None


@dataclass
class BitType(ClassicalType):
    """
    Node representing the classical ``bit`` type, with an optional size.

    Example::

        bit[8]
        creg[8]
    """

    size: Optional[Expression] = None


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

    base_type: Union[
        IntType, UintType, FloatType, AngleType, DurationType, BitType, BoolType, ComplexType
    ]
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

    base_type: Union[
        IntType, UintType, FloatType, AngleType, DurationType, BitType, BoolType, ComplexType
    ]
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

    name: str


@dataclass
class CalibrationStatement(Statement):
    """An inline ``cal`` statement for embedded pulse-grammar interactions.

    Example::

        cal {
            shift_phase(drive($0), theta);
        }
    """

    body: str


@dataclass
class CalibrationDefinition(Statement):
    """
    Calibration definition

    Example::

        defcal rz(angle[20] theta) q {
            shift_phase drive(q), -theta;
        }
    """

    name: Identifier
    arguments: List[Union[ClassicalArgument, Expression]]
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
    body: List[Statement]
    return_type: Optional[ClassicalType] = None


@dataclass
class QuantumArgument(QASMNode):
    """
    Quantum argument for a subroutine declaration
    """

    name: Identifier
    size: Optional[Expression] = None


@dataclass
class ReturnStatement(Statement):
    """
    Classical or quantum return statement

    Example::

        return measure q;

        return a + b

    """

    expression: Optional[Union[Expression, QuantumMeasurement]] = None


class BreakStatement(Statement):
    """
    Break statement

    Example::

        break;
    """


class ContinueStatement(Statement):
    """
    Continue statement

    Example::

        continue;
    """


class EndStatement(Statement):
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

    type: ClassicalType
    identifier: Identifier
    set_declaration: Union[RangeDefinition, DiscreteSet, Expression]
    block: List[Statement]


@dataclass
class SwitchStatement(Statement):
    """A switch-case statement.

    The literal cases are stored in the `cases` dictionary, in declaration
    order.  Python's `dict` guarantees (for all supported versions of Python)
    that the iteration order will be insertion order, so this field *is*
    ordered.

    The default case, if any, is in the `default` attribute.
    """

    target: Expression
    cases: List[Tuple[List[Expression], CompoundStatement]]
    # Note that `None` is quite different to `[]` in this case; the latter is
    # an explicitly empty body, whereas the absence of a default might mean
    # that the switch is inexhaustive, and a linter might want to complain.
    default: Optional[CompoundStatement]


@dataclass
class DelayInstruction(QuantumStatement):
    """
    Delay instruction

    Example::

        delay[start_stretch] $0;
    """

    duration: Expression
    qubits: List[Union[IndexedIdentifier, Identifier]]


@dataclass
class Box(QuantumStatement):
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
class DurationOf(Expression):
    """
    Duration Of

    Example::

        durationof({x $0;})
    """

    target: List[Statement]


@dataclass
class SizeOf(Expression):
    """``sizeof`` an array's dimensions."""

    target: Expression
    index: Optional[Expression] = None


@dataclass
class AliasStatement(Statement):
    """
    Alias statement

    Example::

        let a = qubits[0];

    """

    target: Identifier
    value: Union[Identifier, Concatenation]


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
class Pragma(QASMNode):
    """
    Pragma
    Example::

        #pragma val1 val2 val3
    """

    command: str
