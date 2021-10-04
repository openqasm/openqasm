from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum, auto


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
class OpenNode:
    """Base class for all OpenQASM 3 nodes"""

    span: Optional[Span] = field(init=False, default=None, compare=False)
    """
    The span(location) of the node in the source code.
    Because not all the nodes are generated from source, the span is optional.
    To make it easier to write unit test, we exclude span from the generated __eq__().
    """


@dataclass
class Program(OpenNode):
    """
    An entire OpenQASM 3 program represented by a list of top level statements
    """

    statements: List[Statement]
    version: str = field(init=False, default="")
    includes: List[Include] = field(init=False, default_factory=list)
    io_variables: List[IODeclaration] = field(init=False, default_factory=list)


@dataclass
class Include(OpenNode):
    """
    An include statement
    """

    filename: str


class Statement(OpenNode):
    """A statement: anything that can appear on its own line"""


@dataclass
class AliasStatement(Statement):
    """
    Alias statement

    Example::

        let a = qubits[0];

    """

    target: Identifier
    value: Union[IndexIdentifier, Identifier]


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

    qubit: Qubit
    designator: Optional[Expression]


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


class Expression(OpenNode):
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
class Qubit(Identifier):
    """
    A qubit

    Example::

        qubit q;

        q  // <- Qubit

    """


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
class IndexExpression(Expression):
    """
    An index expression.

    This is used to represent the following unlabeled line in the grammar:

    expressionTerminator
        : ...
        | expressionTerminator LBRACKET expression RBRACKET

    Example::

        q[1]

        q // <- expression
        1 // <- index_expression
    """

    expression: Expression
    index_expression: Expression


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
    qubits: List[Union[IndexIdentifier, Identifier]]


class GateModifierName(Enum):
    inv = auto()
    pow = auto()
    ctrl = auto()
    negctrl = auto()


@dataclass
class QuantumGateModifier(OpenNode):
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
    qubits: List[Union[IndexIdentifier, Identifier]]


@dataclass
class QuantumMeasurement(QuantumInstruction):
    """
    A quantum measurement instruction

    Example::

        measure q;
    """

    qubit: Union[IndexIdentifier, Identifier]


@dataclass
class QuantumReset(QuantumInstruction):
    """
    A reset instruction.

    Example::

        reset q;
    """

    qubits: List[Union[IndexIdentifier, Identifier]]


@dataclass
class QuantumBarrier(QuantumInstruction):
    """
    A quantum barrier instruction

    Example::

        barrier q;
    """

    qubits: List[Union[IndexIdentifier, Identifier]]


@dataclass
class QuantumMeasurementAssignment(Statement):
    """
    A quantum measurement assignment statement

    Example::

        c = measure q;
    """

    lhs: Union[IndexIdentifier, Identifier]
    measure_instruction: QuantumMeasurement


@dataclass
class ClassicalArgument(OpenNode):
    """
    Classical argument for a gate or subroutine declaration
    """

    type: ClassicalType
    name: Identifier


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

        const n = 10;
    """

    identifier: Identifier
    init_expression: Expression


class ClassicalType(OpenNode):
    """
    Base class for classical type
    """


@dataclass
class IntType(ClassicalType):
    """
    Class for signed int type with a designator.

    Example:

        int[8]
        int[16]
    """

    designator: Optional[Expression]


@dataclass
class UintType(ClassicalType):
    """
    Class for unsigned int type with a designator.

    Example:

        uint[8]
        uint[16]
    """

    designator: Optional[Expression]


@dataclass
class FloatType(ClassicalType):
    """
    Class for float type with a designator.

    Example:

        float[8]
        float[16]
    """

    designator: Optional[Expression]


@dataclass
class AngleType(ClassicalType):
    """
    Class for angle type with a designator.

    Example:

        angle[8]
        angle[16]
    """

    designator: Optional[Expression]


@dataclass
class BitType(ClassicalType):
    """
    Bit type

    Example::

        bit[8]
        creg[8]
    """

    designator: Optional[Expression]


class BoolType(ClassicalType):
    """
    Class for Boolean type.
    """


class DurationType(ClassicalType):
    """
    Class for duration type.
    """


class StretchType(ClassicalType):
    """
    Class for stretch type.
    """


@dataclass
class ComplexType(ClassicalType):
    """
    Complex Type. Its real and imaginary parts are based on other classical types.

    Example::

        complex[int[32]]
        complex[float[32]]
    """

    base_type: Union[IntType, UintType, FloatType, AngleType]


class IndexIdentifier(OpenNode):
    """
    Quantum or classical identifier,
    indexed or not indexed.

    #TODO: we will have to update IndexExpression,
    then IndexIdentifier will be subclass of Expression.

    Example::

        q
        b
        b[1]
        b[3:5]
        b || c
    """


@dataclass
class Subscript(IndexIdentifier):
    """
    Indexed identifier with an integer
    as subscript.

    Example:

        segments[0]
        qubits[1]
    """

    name: str
    index: Expression


@dataclass
class Selection(IndexIdentifier):
    """
    Indexed identifier with multiple integers
    as subscript.

    Example::

        segments[1, 2]
        qubits[1, 2, 3]
    """

    name: str
    indices: List[Expression]


@dataclass
class Slice(IndexIdentifier):
    """
    Indexed identifier with a range
    as subscript.

    Example::

        segments[1:2]
        qubits[1:10:1]
    """

    name: str
    range: RangeDefinition


@dataclass
class RangeDefinition(OpenNode):
    """
    Range definition.

    Example::

        [1:2]
        [1:1:10]
        [:]
    """

    start: Optional[Expression]
    end: Optional[Expression]
    step: Optional[Expression]


@dataclass
class Concatenation(IndexIdentifier):
    """
    Combination of two arrays.

    Example::

        segment1 || segment2
        qubits[0:10] || qubits[15:20]
    """

    lhs: Union[IndexIdentifier, Identifier]
    rhs: Union[IndexIdentifier, Identifier]


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
    qubits: List[Qubit]
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
class QuantumArgument(OpenNode):
    """
    Quantum argument in subroutine definition

    Example::

        qubit q

        qubit[4] q

    """

    qubit: Qubit
    designator: Optional[Expression]


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
    Branch (if) statement

    Example::

        if(temp == 1) { ry(-pi / 2) scratch[0]; } else continue;

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

    for i in [0: 2] { majority a[i], b[i + 1], a[i + 1]; }

    """

    loop_variable: Identifier
    set_declaration: Union[RangeDefinition, List[Expression], Identifier]
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
    qubits: List[Union[IndexIdentifier, Identifier]]


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
class DurationOf(OpenNode):
    """
    Duration Of

    Example::

        durationof({x $0;})

    """

    target: Union[Identifier, List[QuantumStatement]]


AssignmentOperator = Enum("AssignmentOperator", "= += -= *= /= &= |= ~= ^= <<= >>= %= **=")


@dataclass
class ClassicalAssignment(Statement):
    """
    Classical assignment

    Example::

        a[0] = 1;

    """

    lvalue: Union[Identifier, Subscript]
    op: AssignmentOperator
    rvalue: Expression
