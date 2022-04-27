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
    BoolType,
    BooleanLiteral,
    Box,
    BranchingStatement,
    CalibrationDefinition,
    CalibrationGrammarDeclaration,
    Cast,
    ClassicalArgument,
    ClassicalAssignment,
    ClassicalDeclaration,
    ComplexType,
    Concatenation,
    Constant,
    ConstantName,
    ContinueStatement,
    DelayInstruction,
    DiscreteSet,
    DurationLiteral,
    DurationOf,
    DurationType,
    EndStatement,
    ExpressionStatement,
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
    QuantumGate,
    QuantumGateDefinition,
    QuantumGateModifier,
    QuantumMeasurement,
    QuantumMeasurementAssignment,
    QuantumPhase,
    QubitDeclaration,
    RangeDefinition,
    RealLiteral,
    ReturnStatement,
    StretchType,
    StringLiteral,
    SubroutineDefinition,
    TimeUnit,
    UintType,
    UnaryExpression,
    UnaryOperator,
)
from openqasm3.parser import parse, Span
from openqasm3.visitor import QASMVisitor


class SpanGuard(QASMVisitor):
    """Ensure that we did not forget to set spans when we add new AST nodes"""

    def visit(self, node: QASMNode):
        try:
            assert node.span is not None
            return super().visit(node)
        except AssertionError as e:
            raise Exception(f"The span of {type(node)} is None.") from e


def test_qubit_declaration():
    p = """
    qubit q;
    qubit[4] a;
    """.strip()
    program = parse(p)
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
        statements=[
            ClassicalDeclaration(BitType(None), Identifier("c"), None),
            QubitDeclaration(qubit=Identifier(name="a"), size=None),
        ]
    )
    SpanGuard().visit(program)


def test_complex_declaration():
    p = """
    complex[int[24]] iq;
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            ClassicalDeclaration(
                ComplexType(base_type=IntType(IntegerLiteral(24))),
                Identifier("iq"),
                None,
            ),
        ]
    )
    SpanGuard().visit(program)
    context_declaration = program.statements[0]
    assert context_declaration.span == Span(1, 0, 1, 19)


def test_array_declaration():
    p = """
    array[uint[8], 2] a;
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
    assert program == Program(
        statements=[
            ClassicalDeclaration(
                type=ArrayType(base_type=UintType(eight), dimensions=[two]),
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


def test_single_gatecall():
    p = """
    h q;
    """.strip()
    program = parse(p)
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
        statements=[
            QuantumGateDefinition(
                name=Identifier("rz"),
                arguments=[Identifier(name="λ")],
                qubits=[Identifier(name="a")],
                body=[
                    QuantumPhase(
                        quantum_gate_modifiers=[],
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
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
        statements=[AliasStatement(target=Identifier(name="a"), value=Identifier(name="b"))]
    )
    SpanGuard().visit(program)
    alias_statement = program.statements[0]
    assert alias_statement.span == Span(1, 0, 1, 9)
    assert alias_statement.target.span == Span(1, 4, 1, 4)
    assert alias_statement.value.span == Span(1, 8, 1, 8)


def test_primary_expression():
    p = """
    π;
    pi;
    5;
    2.0;
    true;
    false;
    a;
    "openqasm";
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
    assert program == Program(
        statements=[
            ExpressionStatement(expression=Constant(name=ConstantName.pi)),
            ExpressionStatement(expression=Constant(name=ConstantName.pi)),
            ExpressionStatement(expression=IntegerLiteral(5)),
            ExpressionStatement(expression=RealLiteral(2.0)),
            ExpressionStatement(expression=BooleanLiteral(True)),
            ExpressionStatement(expression=BooleanLiteral(False)),
            ExpressionStatement(expression=Identifier("a")),
            ExpressionStatement(expression=StringLiteral("openqasm")),
            ExpressionStatement(expression=FunctionCall(Identifier("sin"), [RealLiteral(0.0)])),
            ExpressionStatement(expression=FunctionCall(Identifier("foo"), [Identifier("x")])),
            ExpressionStatement(expression=DurationLiteral(1.1, TimeUnit.ns)),
            ExpressionStatement(expression=DurationLiteral(0.3, TimeUnit.us)),
            ExpressionStatement(expression=DurationLiteral(1e-4, TimeUnit.us)),
            ExpressionStatement(expression=Identifier("x")),
            ExpressionStatement(expression=IndexExpression(Identifier("q"), [IntegerLiteral(1)])),
            ExpressionStatement(
                expression=Cast(
                    IntType(size=IntegerLiteral(1)),
                    [Identifier("x")],
                )
            ),
            ExpressionStatement(
                expression=Cast(
                    BoolType(),
                    [Identifier("x")],
                )
            ),
            ExpressionStatement(expression=FunctionCall(Identifier("sizeof"), [Identifier("a")])),
            ExpressionStatement(
                expression=FunctionCall(Identifier("sizeof"), [Identifier("a"), IntegerLiteral(1)]),
            ),
        ]
    )


def test_unary_expression():
    p = """
    ~b;
    !b;
    -i;
    """.strip()

    program = parse(p)
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
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
    assert program == Program(
        statements=[
            QuantumMeasurementAssignment(
                target=None, measure_instruction=QuantumMeasurement(qubit=Identifier("q"))
            ),
            QuantumMeasurementAssignment(
                target=IndexedIdentifier(
                    name=Identifier(name="c"),
                    indices=[[IntegerLiteral(value=0)]],
                ),
                measure_instruction=QuantumMeasurement(qubit=Identifier("q")),
            ),
            QuantumMeasurementAssignment(
                target=IndexedIdentifier(
                    name=Identifier(name="c"),
                    indices=[[IntegerLiteral(value=0)]],
                ),
                measure_instruction=QuantumMeasurement(
                    qubit=IndexedIdentifier(
                        name=Identifier("q"),
                        indices=[[IntegerLiteral(value=0)]],
                    ),
                ),
            ),
        ]
    )
    SpanGuard().visit(program)


def test_calibration_grammar_declaration():
    p = """
    defcalgrammar "openpulse";
    """.strip()
    program = parse(p)
    assert program == Program(statements=[CalibrationGrammarDeclaration("openpulse")])
    SpanGuard().visit(program)


def test_calibration_definition():
    p = """
    defcal rz(angle[20] theta) $q -> bit { return shift_phase drive($q), -theta; }
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            CalibrationDefinition(
                name=Identifier("rz"),
                arguments=[
                    ClassicalArgument(
                        type=AngleType(size=IntegerLiteral(20)),
                        name=Identifier("theta"),
                    )
                ],
                qubits=[Identifier("$q")],
                return_type=BitType(None),
                body="return shift_phase drive ( $q ) , - theta ;",
            )
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
    assert program == Program(
        statements=[
            SubroutineDefinition(
                name=Identifier("ymeasure"),
                arguments=[QuantumArgument(qubit=Identifier("q"), size=None)],
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
    def a(qubit b, const array[uint[8], 2, 3] c) {}
    def a(mutable array[uint[8], #dim=5] b, const array[uint[8], 5] c) {}
    """.strip()
    program = parse(p)
    a, b, c = Identifier(name="a"), Identifier(name="b"), Identifier(name="c")
    SpanGuard().visit(program)
    assert program == Program(
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
                    QuantumArgument(qubit=c, size=None),
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
                    QuantumArgument(qubit=c, size=IntegerLiteral(2)),
                ],
                return_type=ComplexType(FloatType(IntegerLiteral(64))),
                body=[],
            ),
            SubroutineDefinition(
                name=a,
                arguments=[
                    QuantumArgument(qubit=b, size=None),
                    ClassicalArgument(
                        type=ArrayReferenceType(
                            base_type=UintType(IntegerLiteral(8)),
                            dimensions=[IntegerLiteral(2), IntegerLiteral(3)],
                        ),
                        name=c,
                        access=AccessControl.CONST,
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
                        access=AccessControl.MUTABLE,
                    ),
                    ClassicalArgument(
                        type=ArrayReferenceType(
                            base_type=UintType(IntegerLiteral(8)),
                            dimensions=[IntegerLiteral(5)],
                        ),
                        name=c,
                        access=AccessControl.CONST,
                    ),
                ],
                return_type=None,
                body=[],
            ),
        ]
    )


def test_branch_statement():
    p = """
    if(temp == 1) { ry(pi / 2) q; } else continue;
    """.strip()
    program = parse(p)
    assert program == Program(
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
                                lhs=Constant(ConstantName.pi),
                                rhs=IntegerLiteral(2),
                            )
                        ],
                        qubits=[Identifier("q")],
                    ),
                ],
                else_block=[ContinueStatement()],
            )
        ]
    )
    SpanGuard().visit(program)


def test_for_in_loop():
    p = """
    for i in [0: 2] { majority a[i], b[i + 1], a[i + 1]; }
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            ForInLoop(
                loop_variable=Identifier("i"),
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
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_delay_instruction():
    p = """
    delay[start_stretch] $0;
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            DelayInstruction(
                arguments=[],
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
    assert program == Program(
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
    assert program == Program(
        statements=[
            Box(
                duration=Identifier("maxdur"),
                body=[
                    DelayInstruction(
                        arguments=[],
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
        for i in [1:2]{
            h $0;
            cx $0, $1;
        }
        x $0;
    }
    """.strip()
    program = parse(p)
    print(parse(p))
    assert program == Program(
        statements=[
            Box(
                duration=Identifier("maxdur"),
                body=[
                    DelayInstruction(
                        arguments=[],
                        duration=Identifier("start_stretch"),
                        qubits=[Identifier("$0")],
                    ),
                    ForInLoop(
                        loop_variable=Identifier(name="i"),
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
    durationof({x $0;})
    """.strip()
    program = parse(p)
    assert program == Program(
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
    assert program == Program(
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
    input angle[16] variable1;
    output angle[16] variable2;
    """.strip()
    program = parse(p)
    expected = "3.1"
    assert program.version == expected
    assert program.includes == [Include("qelib1.inc")]
    assert program.io_variables == [
        IODeclaration(
            io_identifier=IOKeyword["input"],
            type=AngleType(size=IntegerLiteral(value=16)),
            identifier=Identifier(name="variable1"),
            init_expression=None,
        ),
        IODeclaration(
            io_identifier=IOKeyword["output"],
            type=AngleType(size=IntegerLiteral(value=16)),
            identifier=Identifier(name="variable2"),
            init_expression=None,
        ),
    ]


def test_end_statement():
    p = """
    end;
    """.strip()
    program = parse(p)
    assert program == Program(statements=[EndStatement()])
    SpanGuard().visit(program)


def test_pramga():
    p = """
    #pragma {verbatim;}
    #pragma {my_statement1; my_statement2;}
    end;
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            Pragma(statements=[ExpressionStatement(Identifier("verbatim"))]),
            Pragma(
                statements=[
                    ExpressionStatement(Identifier("my_statement1")),
                    ExpressionStatement(Identifier("my_statement2")),
                ]
            ),
            EndStatement(),
        ]
    )
    SpanGuard().visit(program)
