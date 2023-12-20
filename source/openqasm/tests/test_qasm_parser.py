import dataclasses
import textwrap
import pytest

from openqasm3.ast import (
    AccessControl,
    AliasStatement,
    AngleType,
    Annotation,
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
    CalibrationDefinition,
    CalibrationGrammarDeclaration,
    CalibrationStatement,
    Cast,
    ClassicalArgument,
    ClassicalAssignment,
    ClassicalDeclaration,
    ComplexType,
    CompoundStatement,
    Concatenation,
    ContinueStatement,
    DelayInstruction,
    DiscreteSet,
    DurationLiteral,
    DurationOf,
    DurationType,
    EndStatement,
    ExpressionStatement,
    ExternArgument,
    ExternDeclaration,
    FloatLiteral,
    FloatType,
    ForInLoop,
    FunctionCall,
    GateModifierName,
    IODeclaration,
    IOKeyword,
    Identifier,
    ImaginaryLiteral,
    Include,
    IndexExpression,
    IndexedIdentifier,
    IntType,
    IntegerLiteral,
    Pragma,
    Program,
    QASMNode,
    QuantumArgument,
    QuantumGate,
    QuantumGateDefinition,
    QuantumGateModifier,
    QuantumMeasurement,
    QuantumMeasurementStatement,
    QuantumPhase,
    QubitDeclaration,
    RangeDefinition,
    ReturnStatement,
    SizeOf,
    Span,
    StretchType,
    SubroutineDefinition,
    SwitchStatement,
    TimeUnit,
    UintType,
    UnaryExpression,
    UnaryOperator,
)
from openqasm3.parser import parse, QASM3ParsingError
from openqasm3.visitor import QASMVisitor


def _with_annotations(node, annotations):
    """Helper function to attach annotations to a QASMNode, since the current
    dataclass-based implementation does not allow us to easily add the
    annotations field (with a default) to statement constructors."""
    node.annotations = annotations
    return node


class SpanGuard(QASMVisitor):
    """Ensure that we did not forget to set spans when we add new AST nodes"""

    def visit(self, node: QASMNode):
        assert node.span is not None
        return super().visit(node)


def _remove_spans(node):
    """Return a new ``QASMNode`` with all spans recursively set to ``None`` to
    reduce noise in test failure messages."""
    if isinstance(node, list):
        return [_remove_spans(item) for item in node]
    if not isinstance(node, QASMNode):
        return node
    kwargs = {}
    no_init = {}
    for field in dataclasses.fields(node):
        if field.name == "span":
            continue
        target = kwargs if field.init else no_init
        target[field.name] = _remove_spans(getattr(node, field.name))
    out = type(node)(**kwargs)
    for attribute, value in no_init.items():
        setattr(out, attribute, value)
    return out


def test_qubit_declaration():
    p = """
    qubit q;
    qubit[4] a;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QubitDeclaration(qubit=Identifier(name="q"), size=None),
            QubitDeclaration(
                qubit=Identifier(name="a"),
                size=IntegerLiteral(4),
            ),
        ]
    )
    SpanGuard().visit(program)
    qubit_declaration = program.statements[0]
    assert qubit_declaration.span == Span(1, 0, 1, 7)
    assert qubit_declaration.qubit.span == Span(1, 6, 1, 6)


def test_bit_declaration():
    p = """
    bit c;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[ClassicalDeclaration(BitType(None), Identifier("c"), None)]
    )
    SpanGuard().visit(program)
    classical_declaration = program.statements[0]
    assert classical_declaration.span == Span(1, 0, 1, 5)


def test_qubit_and_bit_declaration():
    p = """
    bit c;
    qubit a;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(BitType(None), Identifier("c"), None),
            QubitDeclaration(qubit=Identifier(name="a"), size=None),
        ]
    )
    SpanGuard().visit(program)


def test_integer_declaration():
    p = """
    uint[16] a = 100;
    uint[16] a = 0b0110_0100;
    int[16] a = 0B01100100;
    uint[16] a = 0o144;
    uint[16] a = 0xff_64;
    int[16] a = 0X19_a_b;
    """.strip()
    program = parse(p)
    uint16 = UintType(IntegerLiteral(16))
    int16 = IntType(IntegerLiteral(16))
    a = Identifier("a")
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(uint16, a, IntegerLiteral(100)),
            ClassicalDeclaration(uint16, a, IntegerLiteral(0b0110_0100)),
            ClassicalDeclaration(int16, a, IntegerLiteral(0b0110_0100)),
            ClassicalDeclaration(uint16, a, IntegerLiteral(0o144)),
            ClassicalDeclaration(uint16, a, IntegerLiteral(0xFF64)),
            ClassicalDeclaration(int16, a, IntegerLiteral(0x19AB)),
        ]
    )
    SpanGuard().visit(program)


def test_float_declaration():
    p = """
    float[64] a = 125.;
    float[64] a = 1_25.;
    float[64] a = 1_25.e1;
    float[64] a = .1_25;
    float[64] a = .125e1;
    float[64] a = .125e+1;
    float[64] a = .125e-1;
    float[64] a = 125.125e1_25;
    """.strip()
    program = parse(p)
    float64 = FloatType(IntegerLiteral(64))
    a = Identifier("a")
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(float64, a, FloatLiteral(125.0)),
            ClassicalDeclaration(float64, a, FloatLiteral(125.0)),
            ClassicalDeclaration(float64, a, FloatLiteral(1250.0)),
            ClassicalDeclaration(float64, a, FloatLiteral(0.125)),
            ClassicalDeclaration(float64, a, FloatLiteral(1.25)),
            ClassicalDeclaration(float64, a, FloatLiteral(1.25)),
            ClassicalDeclaration(float64, a, FloatLiteral(0.0125)),
            ClassicalDeclaration(float64, a, FloatLiteral(125.125e125)),
        ]
    )
    SpanGuard().visit(program)


def test_simple_type_declarations():
    p = """
    int[32] a;
    int[const_expr] a;
    int a;
    uint[32] a = 1;
    uint[const_expr] a;
    uint a = 1;
    float[32] a;
    float a;
    angle[32] a;
    angle a;
    """.strip()
    program = parse(p)
    a = Identifier("a")
    one = IntegerLiteral(1)
    thirty_two = IntegerLiteral(32)
    const_expr = Identifier("const_expr")
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(type=IntType(size=thirty_two), identifier=a, init_expression=None),
            ClassicalDeclaration(type=IntType(size=const_expr), identifier=a, init_expression=None),
            ClassicalDeclaration(type=IntType(size=None), identifier=a, init_expression=None),
            ClassicalDeclaration(type=UintType(size=thirty_two), identifier=a, init_expression=one),
            ClassicalDeclaration(
                type=UintType(size=const_expr), identifier=a, init_expression=None
            ),
            ClassicalDeclaration(type=UintType(size=None), identifier=a, init_expression=one),
            ClassicalDeclaration(
                type=FloatType(size=thirty_two), identifier=a, init_expression=None
            ),
            ClassicalDeclaration(type=FloatType(size=None), identifier=a, init_expression=None),
            ClassicalDeclaration(
                type=AngleType(size=thirty_two), identifier=a, init_expression=None
            ),
            ClassicalDeclaration(type=AngleType(size=None), identifier=a, init_expression=None),
        ],
    )
    SpanGuard().visit(program)


def test_complex_declaration():
    p = """
    complex[float[64]] a;
    complex[float] fq;
    complex implicit;
    complex[float[64]] imag = 1im;
    complex[float[64]] c64 = 2+9.2im;
    complex[float] a_float = 2.1+0im;
    complex c = 0-9 im ;
    complex rl = 2.1im - 0.2;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(
                ComplexType(base_type=FloatType(IntegerLiteral(64))),
                Identifier("a"),
                None,
            ),
            ClassicalDeclaration(
                ComplexType(base_type=FloatType(size=None)),
                Identifier("fq"),
                None,
            ),
            ClassicalDeclaration(
                ComplexType(base_type=None),
                Identifier("implicit"),
                None,
            ),
            ClassicalDeclaration(
                ComplexType(
                    base_type=FloatType(size=IntegerLiteral(64)),
                ),
                Identifier("imag"),
                ImaginaryLiteral(1.0),
            ),
            ClassicalDeclaration(
                ComplexType(
                    base_type=FloatType(size=IntegerLiteral(64)),
                ),
                Identifier("c64"),
                BinaryExpression(
                    BinaryOperator["+"],
                    IntegerLiteral(2),
                    ImaginaryLiteral(9.2),
                ),
            ),
            ClassicalDeclaration(
                ComplexType(
                    base_type=FloatType(size=None),
                ),
                Identifier("a_float"),
                BinaryExpression(
                    BinaryOperator["+"],
                    FloatLiteral(2.1),
                    ImaginaryLiteral(0),
                ),
            ),
            ClassicalDeclaration(
                ComplexType(
                    base_type=None,
                ),
                Identifier("c"),
                BinaryExpression(
                    BinaryOperator["-"],
                    IntegerLiteral(0),
                    ImaginaryLiteral(9.0),
                ),
            ),
            ClassicalDeclaration(
                ComplexType(
                    base_type=None,
                ),
                Identifier("rl"),
                BinaryExpression(
                    BinaryOperator["-"],
                    ImaginaryLiteral(2.1),
                    FloatLiteral(0.2),
                ),
            ),
        ]
    )
    SpanGuard().visit(program)
    context_declaration = program.statements[0]
    assert context_declaration.span == Span(1, 0, 1, 20)


def test_array_declaration():
    p = """
    array[uint[8], 2] a;
    array[uint, 2] a;
    array[int[8], 2] a = {1, 1};
    array[bit, 2] a = b;
    array[float[32], 2, 2] a;
    array[complex[float[64]], 2, 2] a = {{1, 1}, {2, 2}};
    array[uint[8], 2, 2] a = {b, b};
    """.strip()
    program = parse(p)
    a, b = Identifier("a"), Identifier("b")
    one, two, eight = IntegerLiteral(1), IntegerLiteral(2), IntegerLiteral(8)
    SpanGuard().visit(program)
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(
                type=ArrayType(base_type=UintType(eight), dimensions=[two]),
                identifier=a,
                init_expression=None,
            ),
            ClassicalDeclaration(
                type=ArrayType(base_type=UintType(size=None), dimensions=[two]),
                identifier=a,
                init_expression=None,
            ),
            ClassicalDeclaration(
                type=ArrayType(base_type=IntType(eight), dimensions=[two]),
                identifier=a,
                init_expression=ArrayLiteral([one, one]),
            ),
            ClassicalDeclaration(
                type=ArrayType(base_type=BitType(size=None), dimensions=[two]),
                identifier=a,
                init_expression=b,
            ),
            ClassicalDeclaration(
                type=ArrayType(
                    base_type=FloatType(IntegerLiteral(32)),
                    dimensions=[two, two],
                ),
                identifier=a,
                init_expression=None,
            ),
            ClassicalDeclaration(
                type=ArrayType(
                    base_type=ComplexType(FloatType(IntegerLiteral(64))),
                    dimensions=[two, two],
                ),
                identifier=a,
                init_expression=ArrayLiteral(
                    [ArrayLiteral([one, one]), ArrayLiteral([two, two])],
                ),
            ),
            ClassicalDeclaration(
                type=ArrayType(base_type=UintType(eight), dimensions=[two, two]),
                identifier=a,
                init_expression=ArrayLiteral([b, b]),
            ),
        ],
    )


def test_extern_declarations():
    p = """
    extern f();
    extern f() -> bool;
    extern f(bool);
    extern f(int[32], uint[32]);
    extern f(mutable array[complex[float[64]], N_ELEMENTS]) -> int[2 * INT_SIZE];
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExternDeclaration(
                name=Identifier(name="f"),
                arguments=[],
            ),
            ExternDeclaration(
                name=Identifier(name="f"),
                arguments=[],
                return_type=BoolType(),
            ),
            ExternDeclaration(
                name=Identifier(name="f"),
                arguments=[
                    ExternArgument(type=BoolType()),
                ],
            ),
            ExternDeclaration(
                name=Identifier(name="f"),
                arguments=[
                    ExternArgument(type=IntType(IntegerLiteral(32))),
                    ExternArgument(type=UintType(IntegerLiteral(32))),
                ],
            ),
            ExternDeclaration(
                name=Identifier(name="f"),
                arguments=[
                    ExternArgument(
                        type=ArrayReferenceType(
                            base_type=ComplexType(FloatType(IntegerLiteral(64))),
                            dimensions=[Identifier(name="N_ELEMENTS")],
                        ),
                        access=AccessControl["mutable"],
                    ),
                ],
                return_type=IntType(
                    size=BinaryExpression(
                        op=BinaryOperator["*"],
                        lhs=IntegerLiteral(2),
                        rhs=Identifier(name="INT_SIZE"),
                    )
                ),
            ),
        ]
    )
    SpanGuard().visit(program)


def test_single_gatecall():
    p = """
    h q;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumGate(
                modifiers=[], name=Identifier("h"), arguments=[], qubits=[Identifier(name="q")]
            )
        ]
    )
    SpanGuard().visit(program)
    quantum_gate = program.statements[0]
    assert quantum_gate.span == Span(1, 0, 1, 3)
    assert quantum_gate.qubits[0].span == Span(1, 2, 1, 2)


def test_gate_definition1():
    p = """
gate xy q {
    x q;
    y q;
}
""".strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumGateDefinition(
                Identifier("xy"),
                [],
                [Identifier("q")],
                [
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("x"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("y"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                ],
            )
        ],
    )
    SpanGuard().visit(program)
    gate_declaration = program.statements[0]
    assert gate_declaration.span == Span(1, 0, 4, 0)
    assert gate_declaration.qubits[0].span == Span(1, 8, 1, 8)


def test_gate_definition2():
    p = """
gate majority a, b, c {
     cx c, b;
     cx c, a;
     ccx a, b, c;
}""".strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumGateDefinition(
                name=Identifier("majority"),
                arguments=[],
                qubits=[
                    Identifier(name="a"),
                    Identifier(name="b"),
                    Identifier(name="c"),
                ],
                body=[
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("cx"),
                        arguments=[],
                        qubits=[Identifier(name="c"), Identifier(name="b")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("cx"),
                        arguments=[],
                        qubits=[Identifier(name="c"), Identifier(name="a")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("ccx"),
                        arguments=[],
                        qubits=[
                            Identifier(name="a"),
                            Identifier(name="b"),
                            Identifier(name="c"),
                        ],
                    ),
                ],
            )
        ],
    )
    SpanGuard().visit(program)
    gate_declaration = program.statements[0]
    assert gate_declaration.span == Span(1, 0, 5, 0)
    assert gate_declaration.qubits[0].span == Span(1, 14, 1, 14)


def test_gate_definition3():
    p = """
gate rz(λ) a { gphase(-λ/2); U(0, 0, λ) a; }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumGateDefinition(
                name=Identifier("rz"),
                arguments=[Identifier(name="λ")],
                qubits=[Identifier(name="a")],
                body=[
                    QuantumPhase(
                        modifiers=[],
                        argument=BinaryExpression(
                            op=BinaryOperator["/"],
                            lhs=UnaryExpression(
                                op=UnaryOperator["-"], expression=Identifier(name="λ")
                            ),
                            rhs=IntegerLiteral(value=2),
                        ),
                        qubits=[],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("U"),
                        arguments=[
                            IntegerLiteral(value=0),
                            IntegerLiteral(value=0),
                            Identifier(name="λ"),
                        ],
                        qubits=[Identifier(name="a")],
                    ),
                ],
            )
        ]
    )
    SpanGuard().visit(program)
    gate_declaration = program.statements[0]
    assert gate_declaration.span == Span(1, 0, 1, 43)
    assert gate_declaration.arguments[0].span == Span(1, 8, 1, 8)
    assert gate_declaration.qubits[0].span == Span(1, 11, 1, 11)


def test_gate_calls():
    p = """
    qubit q;
    qubit r;
    h q;
    cx q, r;
    inv @ h q;
    """.strip()
    # TODO Add "ctrl @ pow(power) @ phase(theta) q, r;" after we complete expressions
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QubitDeclaration(qubit=Identifier(name="q"), size=None),
            QubitDeclaration(qubit=Identifier(name="r"), size=None),
            QuantumGate(
                modifiers=[], name=Identifier("h"), arguments=[], qubits=[Identifier(name="q")]
            ),
            QuantumGate(
                modifiers=[],
                name=Identifier("cx"),
                arguments=[],
                qubits=[Identifier(name="q"), Identifier(name="r")],
            ),
            QuantumGate(
                modifiers=[QuantumGateModifier(modifier=GateModifierName["inv"], argument=None)],
                name=Identifier("h"),
                arguments=[],
                qubits=[Identifier(name="q")],
            ),
        ],
    )
    SpanGuard().visit(program)


def test_gate_defs():
    p = """
    gate xyz q {
        x q;
        y q;
        z q;
    }
    """.strip()

    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumGateDefinition(
                name=Identifier("xyz"),
                arguments=[],
                qubits=[Identifier(name="q")],
                body=[
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("x"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("y"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("z"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                ],
            )
        ],
    )
    SpanGuard().visit(program)


def test_alias_statement():
    p = """
    let a = b;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[AliasStatement(target=Identifier(name="a"), value=Identifier(name="b"))]
    )
    SpanGuard().visit(program)
    alias_statement = program.statements[0]
    assert alias_statement.span == Span(1, 0, 1, 9)
    assert alias_statement.target.span == Span(1, 4, 1, 4)
    assert alias_statement.value.span == Span(1, 8, 1, 8)


def test_anonymous_scope():
    p = textwrap.dedent(
        """
    {
      int i = 1;
      i = 2;
    }
    """
    ).strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            CompoundStatement(
                statements=[
                    ClassicalDeclaration(
                        type=IntType(),
                        identifier=Identifier("i"),
                        init_expression=IntegerLiteral(1),
                    ),
                    ClassicalAssignment(
                        lvalue=Identifier("i"), op=AssignmentOperator["="], rvalue=IntegerLiteral(2)
                    ),
                ]
            )
        ]
    )
    compound_statement = program.statements[0]
    assert compound_statement.span == Span(1, 0, 4, 0)


def test_primary_expression():
    p = """
    π;
    pi;
    5;
    2.0;
    true;
    false;
    a;
    "0110_0100";
    sin(0.0);
    foo(x);
    1.1ns;
    0.3µs;
    1E-4us;
    (x);
    q[1];
    int[1](x);
    bool(x);
    sizeof(a);
    sizeof(a, 1);
    """.strip()

    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExpressionStatement(expression=Identifier(name="π")),
            ExpressionStatement(expression=Identifier(name="pi")),
            ExpressionStatement(expression=IntegerLiteral(5)),
            ExpressionStatement(expression=FloatLiteral(2.0)),
            ExpressionStatement(expression=BooleanLiteral(True)),
            ExpressionStatement(expression=BooleanLiteral(False)),
            ExpressionStatement(expression=Identifier("a")),
            ExpressionStatement(expression=BitstringLiteral(100, 8)),
            ExpressionStatement(expression=FunctionCall(Identifier("sin"), [FloatLiteral(0.0)])),
            ExpressionStatement(expression=FunctionCall(Identifier("foo"), [Identifier("x")])),
            ExpressionStatement(expression=DurationLiteral(1.1, TimeUnit.ns)),
            ExpressionStatement(expression=DurationLiteral(0.3, TimeUnit.us)),
            ExpressionStatement(expression=DurationLiteral(1e-4, TimeUnit.us)),
            ExpressionStatement(expression=Identifier("x")),
            ExpressionStatement(expression=IndexExpression(Identifier("q"), [IntegerLiteral(1)])),
            ExpressionStatement(expression=Cast(IntType(size=IntegerLiteral(1)), Identifier("x"))),
            ExpressionStatement(expression=Cast(BoolType(), Identifier("x"))),
            ExpressionStatement(expression=SizeOf(Identifier("a"))),
            ExpressionStatement(expression=SizeOf(Identifier("a"), IntegerLiteral(1))),
        ]
    )


def test_unary_expression():
    p = """
    ~b;
    !b;
    -i;
    """.strip()

    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExpressionStatement(
                expression=UnaryExpression(
                    op=UnaryOperator["~"],
                    expression=Identifier(name="b"),
                )
            ),
            ExpressionStatement(
                expression=UnaryExpression(
                    op=UnaryOperator["!"],
                    expression=Identifier(name="b"),
                )
            ),
            ExpressionStatement(
                expression=UnaryExpression(
                    op=UnaryOperator["-"],
                    expression=Identifier(name="i"),
                )
            ),
        ]
    )


def test_binary_expression():
    p = """
    b1 || b2;
    b1 && b2;
    b1 | b2;
    b1 ^ b2;
    b1 & b2;
    b1 != b2;
    i1 >= i2;
    i1 << i2;
    i1 - i2;
    i1 / i2;
    """.strip()

    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["||"],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["&&"],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["|"],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["^"],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["&"],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["!="],
                    lhs=Identifier(name="b1"),
                    rhs=Identifier(name="b2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator[">="],
                    lhs=Identifier(name="i1"),
                    rhs=Identifier(name="i2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["<<"],
                    lhs=Identifier(name="i1"),
                    rhs=Identifier(name="i2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["-"],
                    lhs=Identifier(name="i1"),
                    rhs=Identifier(name="i2"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["/"],
                    lhs=Identifier(name="i1"),
                    rhs=Identifier(name="i2"),
                )
            ),
        ]
    )


def test_binary_expression_precedence():
    p = """
    b1 || b2 && b3;
    b1 | b2 ^ b3;
    b1 != b2 + b3;
    i1 >= i2 + i3;
    i1 - i2 << i3;
    i1 - i2 / i3;
    i1[i2] + -i1[i2];
    -i1 ** i2;
    """.strip()

    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["||"],
                    lhs=Identifier(name="b1"),
                    rhs=BinaryExpression(
                        op=BinaryOperator["&&"],
                        lhs=Identifier(name="b2"),
                        rhs=Identifier(name="b3"),
                    ),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["|"],
                    lhs=Identifier(name="b1"),
                    rhs=BinaryExpression(
                        op=BinaryOperator["^"],
                        lhs=Identifier(name="b2"),
                        rhs=Identifier(name="b3"),
                    ),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["!="],
                    lhs=Identifier(name="b1"),
                    rhs=BinaryExpression(
                        op=BinaryOperator["+"],
                        lhs=Identifier(name="b2"),
                        rhs=Identifier(name="b3"),
                    ),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator[">="],
                    lhs=Identifier(name="i1"),
                    rhs=BinaryExpression(
                        op=BinaryOperator["+"],
                        lhs=Identifier(name="i2"),
                        rhs=Identifier(name="i3"),
                    ),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["<<"],
                    lhs=BinaryExpression(
                        op=BinaryOperator["-"],
                        lhs=Identifier(name="i1"),
                        rhs=Identifier(name="i2"),
                    ),
                    rhs=Identifier(name="i3"),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["-"],
                    lhs=Identifier(name="i1"),
                    rhs=BinaryExpression(
                        op=BinaryOperator["/"],
                        lhs=Identifier(name="i2"),
                        rhs=Identifier(name="i3"),
                    ),
                )
            ),
            ExpressionStatement(
                expression=BinaryExpression(
                    op=BinaryOperator["+"],
                    lhs=IndexExpression(collection=Identifier("i1"), index=[Identifier("i2")]),
                    rhs=UnaryExpression(
                        op=UnaryOperator["-"],
                        expression=IndexExpression(
                            collection=Identifier("i1"),
                            index=[Identifier("i2")],
                        ),
                    ),
                ),
            ),
            ExpressionStatement(
                expression=UnaryExpression(
                    op=UnaryOperator["-"],
                    expression=BinaryExpression(
                        op=BinaryOperator["**"],
                        lhs=Identifier("i1"),
                        rhs=Identifier("i2"),
                    ),
                ),
            ),
        ]
    )


def test_alias_assignment():
    p = """
    let a = b;
    let a = b[0:1];
    let a = b[{0, 1, 2}];
    let a = b ++ c;
    let a = b[{0, 1}] ++ b[2:2:4] ++ c;
    """.strip()
    program = parse(p)
    a, b, c = Identifier(name="a"), Identifier(name="b"), Identifier(name="c")
    assert _remove_spans(program) == Program(
        statements=[
            AliasStatement(target=a, value=b),
            AliasStatement(
                target=a,
                value=IndexExpression(
                    collection=b,
                    index=[
                        RangeDefinition(
                            start=IntegerLiteral(0),
                            end=IntegerLiteral(1),
                            step=None,
                        ),
                    ],
                ),
            ),
            AliasStatement(
                target=a,
                value=IndexExpression(
                    collection=b,
                    index=DiscreteSet(
                        values=[
                            IntegerLiteral(0),
                            IntegerLiteral(1),
                            IntegerLiteral(2),
                        ]
                    ),
                ),
            ),
            AliasStatement(target=a, value=Concatenation(lhs=b, rhs=c)),
            AliasStatement(
                target=a,
                value=Concatenation(
                    lhs=Concatenation(
                        lhs=IndexExpression(
                            collection=b,
                            index=DiscreteSet(
                                values=[IntegerLiteral(0), IntegerLiteral(1)],
                            ),
                        ),
                        rhs=IndexExpression(
                            collection=b,
                            index=[
                                RangeDefinition(
                                    start=IntegerLiteral(2),
                                    end=IntegerLiteral(4),
                                    step=IntegerLiteral(2),
                                ),
                            ],
                        ),
                    ),
                    rhs=c,
                ),
            ),
        ],
    )
    SpanGuard().visit(program)


def test_measurement():
    p = """
    measure q;
    measure q -> c[0];
    c[0] = measure q[0];
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumMeasurementStatement(QuantumMeasurement(qubit=Identifier("q")), target=None),
            QuantumMeasurementStatement(
                measure=QuantumMeasurement(Identifier("q")),
                target=IndexedIdentifier(name=Identifier("c"), indices=[[IntegerLiteral(0)]]),
            ),
            QuantumMeasurementStatement(
                measure=QuantumMeasurement(
                    IndexedIdentifier(Identifier("q"), indices=[[IntegerLiteral(0)]])
                ),
                target=IndexedIdentifier(name=Identifier("c"), indices=[[IntegerLiteral(0)]]),
            ),
        ]
    )
    SpanGuard().visit(program)


@pytest.mark.parametrize("name", ['"openpulse"', "'openpulse'", '"001"'])
def test_calibration_grammar_declaration(name):
    p = f"""
    defcalgrammar {name};
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(statements=[CalibrationGrammarDeclaration(name[1:-1])])
    SpanGuard().visit(program)


def test_calibration_statement():
    p = """
    cal {shift_phase(drive($0), -theta);}
    cal {Outer {nested} outer again.}
    cal {Untokenisable: *$£()"*}
    cal {}
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            CalibrationStatement(body="shift_phase(drive($0), -theta);"),
            CalibrationStatement(body="Outer {nested} outer again."),
            CalibrationStatement(body='Untokenisable: *$£()"*'),
            CalibrationStatement(body=""),
        ],
    )


def test_calibration_definition():
    p = """
    defcal rz(angle[20] theta) q { shift_phase drive(q), -theta; }
    defcal measure $0 -> bit {Outer {nested} outer again.}
    defcal rx(pi / 2) $1 {Untokenisable: *$£()"*}
    defcal cx $0, $1 {}
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            CalibrationDefinition(
                name=Identifier("rz"),
                arguments=[
                    ClassicalArgument(
                        type=AngleType(size=IntegerLiteral(20)),
                        name=Identifier("theta"),
                    )
                ],
                qubits=[Identifier("q")],
                return_type=None,
                body=" shift_phase drive(q), -theta; ",
            ),
            CalibrationDefinition(
                name=Identifier("measure"),
                arguments=[],
                qubits=[Identifier("$0")],
                return_type=BitType(size=None),
                body="Outer {nested} outer again.",
            ),
            CalibrationDefinition(
                name=Identifier("rx"),
                arguments=[
                    BinaryExpression(
                        lhs=Identifier("pi"),
                        op=BinaryOperator["/"],
                        rhs=IntegerLiteral(2),
                    )
                ],
                qubits=[Identifier("$1")],
                return_type=None,
                body='Untokenisable: *$£()"*',
            ),
            CalibrationDefinition(
                name=Identifier("cx"),
                arguments=[],
                qubits=[Identifier("$0"), Identifier("$1")],
                return_type=None,
                body="",
            ),
        ]
    )
    SpanGuard().visit(program)


def test_subroutine_definition():
    p = """
    def ymeasure(qubit q) -> bit {
        s q;
        h q;
        return measure q;
    }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            SubroutineDefinition(
                name=Identifier("ymeasure"),
                arguments=[QuantumArgument(name=Identifier("q"), size=None)],
                return_type=BitType(None),
                body=[
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("s"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("h"),
                        arguments=[],
                        qubits=[Identifier(name="q")],
                    ),
                    ReturnStatement(expression=QuantumMeasurement(qubit=Identifier(name="q"))),
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_subroutine_signatures():
    p = """
    def a(int[8] b) {}
    def a(complex[float[32]] b, qubit c) -> int[32] {}
    def a(bit[5] b, qubit[2] c) -> complex[float[64]] {}
    def a(qubit b, readonly array[uint[8], 2, 3] c) {}
    def a(mutable array[uint[8], #dim=5] b, readonly array[uint[8], 5] c) {}
    """.strip()
    program = parse(p)
    a, b, c = Identifier(name="a"), Identifier(name="b"), Identifier(name="c")
    SpanGuard().visit(program)
    assert _remove_spans(program) == Program(
        statements=[
            SubroutineDefinition(
                name=a,
                arguments=[ClassicalArgument(IntType(IntegerLiteral(8)), b)],
                return_type=None,
                body=[],
            ),
            SubroutineDefinition(
                name=a,
                arguments=[
                    ClassicalArgument(
                        type=ComplexType(FloatType(IntegerLiteral(32))),
                        name=b,
                    ),
                    QuantumArgument(name=c, size=None),
                ],
                return_type=IntType(IntegerLiteral(32)),
                body=[],
            ),
            SubroutineDefinition(
                name=a,
                arguments=[
                    ClassicalArgument(
                        type=BitType(size=IntegerLiteral(5)),
                        name=b,
                    ),
                    QuantumArgument(name=c, size=IntegerLiteral(2)),
                ],
                return_type=ComplexType(FloatType(IntegerLiteral(64))),
                body=[],
            ),
            SubroutineDefinition(
                name=a,
                arguments=[
                    QuantumArgument(name=b, size=None),
                    ClassicalArgument(
                        type=ArrayReferenceType(
                            base_type=UintType(IntegerLiteral(8)),
                            dimensions=[IntegerLiteral(2), IntegerLiteral(3)],
                        ),
                        name=c,
                        access=AccessControl.readonly,
                    ),
                ],
                return_type=None,
                body=[],
            ),
            SubroutineDefinition(
                name=a,
                arguments=[
                    # Note that the first ArrayReferenceType has dimensions of
                    # IntegerLiteral(5) referring to the number of dimensions,
                    # but the second has dimensions [IntegerLiteral(5)] (with a
                    # list), because the sizes of the dimensions are given
                    # explicitly.
                    ClassicalArgument(
                        type=ArrayReferenceType(
                            base_type=UintType(IntegerLiteral(8)),
                            dimensions=IntegerLiteral(5),
                        ),
                        name=b,
                        access=AccessControl.mutable,
                    ),
                    ClassicalArgument(
                        type=ArrayReferenceType(
                            base_type=UintType(IntegerLiteral(8)),
                            dimensions=[IntegerLiteral(5)],
                        ),
                        name=c,
                        access=AccessControl.readonly,
                    ),
                ],
                return_type=None,
                body=[],
            ),
        ]
    )


def test_ambiguous_gate_calls():
    p = """
    gphase(pi);
    fn(pi);
    """.strip()
    program = parse(p)
    SpanGuard().visit(program)
    assert _remove_spans(program) == Program(
        statements=[
            QuantumPhase(modifiers=[], argument=Identifier("pi"), qubits=[]),
            ExpressionStatement(FunctionCall(name=Identifier("fn"), arguments=[Identifier("pi")])),
        ],
    )


def test_branch_statement():
    p = """
    if(temp == 1) { ry(pi / 2) q; } else end;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            BranchingStatement(
                condition=BinaryExpression(
                    op=BinaryOperator["=="],
                    lhs=Identifier("temp"),
                    rhs=IntegerLiteral(1),
                ),
                if_block=[
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("ry"),
                        arguments=[
                            BinaryExpression(
                                op=BinaryOperator["/"],
                                lhs=Identifier(name="pi"),
                                rhs=IntegerLiteral(2),
                            )
                        ],
                        qubits=[Identifier("q")],
                    ),
                ],
                else_block=[EndStatement()],
            )
        ]
    )
    SpanGuard().visit(program)


def test_for_in_loop():
    p = """
    for uint[8] i in [0: 2] { majority a[i], b[i + 1], a[i + 1]; continue; }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ForInLoop(
                type=UintType(IntegerLiteral(8)),
                identifier=Identifier("i"),
                set_declaration=RangeDefinition(
                    start=IntegerLiteral(0), end=IntegerLiteral(2), step=None
                ),
                block=[
                    QuantumGate(
                        modifiers=[],
                        name=Identifier("majority"),
                        arguments=[],
                        qubits=[
                            IndexedIdentifier(
                                name=Identifier(name="a"),
                                indices=[[Identifier("i")]],
                            ),
                            IndexedIdentifier(
                                name=Identifier("b"),
                                indices=[
                                    [
                                        BinaryExpression(
                                            op=BinaryOperator["+"],
                                            lhs=Identifier("i"),
                                            rhs=IntegerLiteral(1),
                                        ),
                                    ]
                                ],
                            ),
                            IndexedIdentifier(
                                name=Identifier(name="a"),
                                indices=[
                                    [
                                        BinaryExpression(
                                            op=BinaryOperator["+"],
                                            lhs=Identifier("i"),
                                            rhs=IntegerLiteral(1),
                                        ),
                                    ],
                                ],
                            ),
                        ],
                    ),
                    ContinueStatement(),
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_switch_simple_cases():
    program = parse("switch (x) { case 0 {} case 1, 2 { z $0; }  }")
    assert _remove_spans(program) == Program(
        statements=[
            SwitchStatement(
                target=Identifier("x"),
                cases=[
                    ([IntegerLiteral(0)], CompoundStatement(statements=[])),
                    (
                        [IntegerLiteral(1), IntegerLiteral(2)],
                        CompoundStatement(
                            statements=[
                                QuantumGate(
                                    modifiers=[],
                                    name=Identifier("z"),
                                    arguments=[],
                                    qubits=[Identifier("$0")],
                                )
                            ]
                        ),
                    ),
                ],
                default=None,
            ),
        ]
    )
    SpanGuard().visit(program)


def test_switch_default_case():
    program = parse("switch (x + 1) { case 0b00 {} default { z $0; }  }")
    assert _remove_spans(program) == Program(
        statements=[
            SwitchStatement(
                target=BinaryExpression(
                    op=BinaryOperator["+"], lhs=Identifier("x"), rhs=IntegerLiteral(1)
                ),
                cases=[
                    ([IntegerLiteral(0)], CompoundStatement(statements=[])),
                ],
                default=CompoundStatement(
                    statements=[
                        QuantumGate(
                            modifiers=[],
                            name=Identifier("z"),
                            arguments=[],
                            qubits=[Identifier("$0")],
                        )
                    ]
                ),
            ),
        ]
    )
    SpanGuard().visit(program)


def test_switch_cases_order():
    program = parse("switch (i) { case 0 {} case 3, 2 {} case 1, 5 {} case 4, 8 {} case 7, 6 {}}")
    expected = [
        [IntegerLiteral(0)],
        [IntegerLiteral(3), IntegerLiteral(2)],
        [IntegerLiteral(1), IntegerLiteral(5)],
        [IntegerLiteral(4), IntegerLiteral(8)],
        [IntegerLiteral(7), IntegerLiteral(6)],
    ]
    switch = program.statements[0]
    # Test that the iteration order maintains the definition order from the program.
    assert [values for values, _ in switch.cases] == expected


def test_switch_no_cases():
    program = parse("switch (x) {}")
    assert _remove_spans(program) == Program(
        statements=[SwitchStatement(target=Identifier("x"), cases=[], default=None)]
    )
    SpanGuard().visit(program)


def test_switch_expression_cases():
    program = parse(
        """
switch (i) {
    case n {}
    case 1 + 1, n - 2 {}
    default {}
}
"""
    )
    assert _remove_spans(program) == Program(
        statements=[
            SwitchStatement(
                target=Identifier("i"),
                cases=[
                    ([Identifier("n")], CompoundStatement(statements=[])),
                    (
                        [
                            BinaryExpression(
                                op=BinaryOperator["+"], lhs=IntegerLiteral(1), rhs=IntegerLiteral(1)
                            ),
                            BinaryExpression(
                                op=BinaryOperator["-"], lhs=Identifier("n"), rhs=IntegerLiteral(2)
                            ),
                        ],
                        CompoundStatement(statements=[]),
                    ),
                ],
                default=CompoundStatement(statements=[]),
            )
        ]
    )
    SpanGuard().visit(program)


def test_switch_rejects_case_after_default():
    program = """
switch (5) {
    case 0 {
    }
    default {
    }
    case 1 {
    }
}
"""
    with pytest.raises(QASM3ParsingError, match="'case' statement after 'default'"):
        parse(program)


def test_switch_rejects_multiple_default():
    program = """
switch (5) {
    case 0 {
    }
    default {
    }
    default {
    }
}
"""
    with pytest.raises(QASM3ParsingError, match="multiple 'default' cases"):
        parse(program)


def test_delay_instruction():
    p = """
    delay[start_stretch] $0;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            DelayInstruction(
                duration=Identifier("start_stretch"),
                qubits=[Identifier("$0")],
            )
        ]
    )
    SpanGuard().visit(program)


def test_no_designator_type():
    p = """
    duration a;
    stretch b;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalDeclaration(
                DurationType(),
                Identifier("a"),
                None,
            ),
            ClassicalDeclaration(StretchType(), Identifier("b"), None),
        ]
    )
    SpanGuard().visit(program)


def test_box():
    p = """
    box [maxdur] {
        delay[start_stretch] $0;
        x $0;
    }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            Box(
                duration=Identifier("maxdur"),
                body=[
                    DelayInstruction(
                        duration=Identifier("start_stretch"),
                        qubits=[Identifier("$0")],
                    ),
                    QuantumGate(
                        modifiers=[], name=Identifier("x"), arguments=[], qubits=[Identifier("$0")]
                    ),
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_quantumloop():
    p = """
    box [maxdur] {
        delay[start_stretch] $0;
        for uint i in [1:2]{
            h $0;
            cx $0, $1;
        }
        x $0;
    }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            Box(
                duration=Identifier("maxdur"),
                body=[
                    DelayInstruction(
                        duration=Identifier("start_stretch"),
                        qubits=[Identifier("$0")],
                    ),
                    ForInLoop(
                        type=UintType(size=None),
                        identifier=Identifier(name="i"),
                        set_declaration=RangeDefinition(
                            start=IntegerLiteral(value=1),
                            end=IntegerLiteral(value=2),
                            step=None,
                        ),
                        block=[
                            QuantumGate(
                                modifiers=[],
                                name=Identifier("h"),
                                arguments=[],
                                qubits=[Identifier(name="$0")],
                            ),
                            QuantumGate(
                                modifiers=[],
                                name=Identifier("cx"),
                                arguments=[],
                                qubits=[Identifier(name="$0"), Identifier(name="$1")],
                            ),
                        ],
                    ),
                    QuantumGate(
                        modifiers=[], name=Identifier("x"), arguments=[], qubits=[Identifier("$0")]
                    ),
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_durationof():
    p = """
    durationof({x $0;});
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ExpressionStatement(
                expression=DurationOf(
                    target=[
                        QuantumGate(
                            modifiers=[],
                            name=Identifier("x"),
                            arguments=[],
                            qubits=[Identifier("$0")],
                        ),
                    ]
                )
            )
        ]
    )
    SpanGuard().visit(program)


def test_classical_assignment():
    p = """
    a[0] = 1;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            ClassicalAssignment(
                lvalue=IndexedIdentifier(
                    name=Identifier("a"),
                    indices=[[IntegerLiteral(value=0)]],
                ),
                op=AssignmentOperator["="],
                rvalue=IntegerLiteral(1),
            )
        ]
    )
    SpanGuard().visit(program)


def test_header():
    p = """
    OPENQASM 3.1;
    include "qelib1.inc";
    include "001";
    input angle[16] variable1;
    output angle[16] variable2;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        version="3.1",
        statements=[
            Include("qelib1.inc"),
            Include("001"),
            IODeclaration(
                io_identifier=IOKeyword["input"],
                type=AngleType(size=IntegerLiteral(value=16)),
                identifier=Identifier(name="variable1"),
            ),
            IODeclaration(
                io_identifier=IOKeyword["output"],
                type=AngleType(size=IntegerLiteral(value=16)),
                identifier=Identifier(name="variable2"),
            ),
        ],
    )
    SpanGuard().visit(program)


def test_end_statement():
    p = """
    end;
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(statements=[EndStatement()])
    SpanGuard().visit(program)


def test_annotations():
    p = """
    @word1 command1
    input uint[32] x;

    @keyword command command

    x = 1;

    @word1 command1
    @word2 command2 32f%^&
    gate my_gate q {}

    @word1 @not_a_separate_annotation uint x;
    int[8] x;

    @word1
    qubit q; uint[4] y;

    @outer
    def fn() {
        @inner1
        int[8] x;
        @inner2 command
        x = 19;
    }
    """.strip()
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            _with_annotations(
                IODeclaration(
                    type=UintType(IntegerLiteral(32)),
                    io_identifier=IOKeyword.input,
                    identifier=Identifier("x"),
                ),
                [Annotation(keyword="word1", command="command1")],
            ),
            # Extra spacing between the annotation and the statement is no problem.
            _with_annotations(
                ClassicalAssignment(
                    lvalue=Identifier("x"),
                    op=AssignmentOperator["="],
                    rvalue=IntegerLiteral(1),
                ),
                [Annotation(keyword="keyword", command="command command")],
            ),
            # Multiple annotations are correctly split in the list.
            _with_annotations(
                QuantumGateDefinition(
                    name=Identifier("my_gate"), arguments=[], qubits=[Identifier("q")], body=[]
                ),
                [
                    Annotation(keyword="word1", command="command1"),
                    Annotation(keyword="word2", command="command2 32f%^&"),
                ],
            ),
            # Nesting the annotation syntax doesn't cause problems.
            _with_annotations(
                ClassicalDeclaration(
                    type=IntType(IntegerLiteral(8)),
                    identifier=Identifier("x"),
                    init_expression=None,
                ),
                [Annotation(keyword="word1", command="@not_a_separate_annotation uint x;")],
            ),
            # Annotations only apply to the next statement, even if the next
            # line contains several statements.
            _with_annotations(
                QubitDeclaration(size=None, qubit=Identifier("q")),
                [Annotation(keyword="word1", command=None)],
            ),
            ClassicalDeclaration(
                type=UintType(IntegerLiteral(4)), identifier=Identifier("y"), init_expression=None
            ),
            # Annotations work both outside and inside nested scopes.
            _with_annotations(
                SubroutineDefinition(
                    name=Identifier("fn"),
                    arguments=[],
                    return_type=None,
                    body=[
                        _with_annotations(
                            ClassicalDeclaration(
                                type=IntType(IntegerLiteral(8)),
                                identifier=Identifier("x"),
                                init_expression=None,
                            ),
                            [Annotation(keyword="inner1", command=None)],
                        ),
                        _with_annotations(
                            ClassicalAssignment(
                                lvalue=Identifier("x"),
                                op=AssignmentOperator["="],
                                rvalue=IntegerLiteral(19),
                            ),
                            [Annotation(keyword="inner2", command="command")],
                        ),
                    ],
                ),
                [Annotation(keyword="outer", command=None)],
            ),
        ],
    )
    SpanGuard().visit(program)


def test_pragma():
    p = """
    #pragma verbatim
    pragma verbatim
    #pragma command arg1 arg2
    pragma command arg1 arg2
    #pragma otherwise_invalid_token 1a2%&
    pragma otherwise_invalid_token 1a2%&
    """  # No strip because all line endings are important for pragmas.
    program = parse(p)
    assert _remove_spans(program) == Program(
        statements=[
            Pragma(command="verbatim"),
            Pragma(command="verbatim"),
            Pragma(command="command arg1 arg2"),
            Pragma(command="command arg1 arg2"),
            Pragma(command="otherwise_invalid_token 1a2%&"),
            Pragma(command="otherwise_invalid_token 1a2%&"),
        ]
    )
    SpanGuard().visit(program)


class TestFailurePaths:
    def test_missing_for_loop_type(self):
        p = "for a in b {};"  # No type of for-loop variable.
        with pytest.raises(QASM3ParsingError):
            parse(p)

    @pytest.mark.parametrize("keyword", ("continue", "break"))
    def test_control_flow_outside_loop(self, keyword):
        message = f"'{keyword}' statement outside loop"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"{keyword};")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"if (true) {keyword};")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"def fn() {{ {keyword}; }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"gate my_gate q {{ {keyword}; }}")

    def test_return_outside_subroutine(self):
        message = f"'return' statement outside subroutine"
        with pytest.raises(QASM3ParsingError, match=message):
            parse("return;")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("if (true) return;")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("gate my_gate q { return; }")

    def test_classical_assignment_in_gate(self):
        message = "cannot assign to classical parameters in a gate"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"int a; gate my_gate q {{ x q; a = 1; }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"int a; gate my_gate q {{ a = 1; }}")

    def test_classical_declaration_in_gate(self):
        message = "cannot declare classical variables in a gate"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"gate my_gate q {{ int a; }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"gate my_gate q {{ int a = 1; }}")

    @pytest.mark.parametrize(
        ("statement", "message"),
        (
            ('defcalgrammar "openpulse";', "'defcalgrammar' statements must be global"),
            ("array[int, 4] arr;", "arrays can only be declared globally"),
            ("def fn() { }", "subroutine definitions must be global"),
            ("extern fn();", "extern declarations must be global"),
            ("gate my_gate q { }", "gate definitions must be global"),
            ('include "stdgates.inc";', "'include' statements must be global"),
            ("input int a;", "'input' declarations must be global"),
            ("output int a;", "'output' declarations must be global"),
            ("qubit q;", "qubit declarations must be global"),
            ("qreg q;", "qubit declarations must be global"),
            ("qreg q[5];", "qubit declarations must be global"),
            ("\npragma command\n", "pragmas must be global"),
        ),
    )
    def test_global_statement_in_nonglobal_context(self, statement, message):
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"for uint[8] i in [0:4] {{ {statement} }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"while (true) {{ {statement} }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"def fn() {{ {statement} }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"if (true) {{ {statement} }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"if (false) x $0; else {{ {statement} }}")
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"def fn() {{ if (true) {{ {statement} }} }}")

    @pytest.mark.parametrize(
        ("statement", "operation"),
        (
            ("measure $0 -> c[0];", "measure"),
            ("measure $0;", "measure"),
            ("reset $0;", "reset"),
        ),
    )
    def test_nonunitary_instructions_in_gate(self, statement, operation):
        message = f"cannot have a non-unitary '{operation}' instruction in a gate"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"bit[5] c; gate my_gate q {{ {statement} }}")

    def test_builtins_with_incorrect_arguments(self):
        message = "'gphase' takes exactly one argument, .*"
        with pytest.raises(QASM3ParsingError, match=message):
            parse("gphase;")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("gphase();")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("gphase(1, 2);")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("ctrl @ gphase $0;")

        message = "'sizeof' needs either one or two arguments"
        with pytest.raises(QASM3ParsingError, match=message):
            parse("sizeof();")
        with pytest.raises(QASM3ParsingError, match=message):
            parse("sizeof(arr, 0, 1);")

    @pytest.mark.parametrize(
        "scalar",
        ("uint", "uint[32]", "bit", "bit[5]", "bool", "duration", "stretch", "complex[float[64]]"),
    )
    def test_complex_with_bad_scalar_type(self, scalar):
        message = "invalid type of complex components"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"complex[{scalar}] f;")

    def test_array_with_bad_scalar_type(self):
        message = "invalid scalar type for array"
        with pytest.raises(QASM3ParsingError, match=message):
            parse(f"array[stretch, 4] arr;")
