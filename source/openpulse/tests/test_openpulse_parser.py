from openqasm3.visitor import QASMVisitor

from openpulse.parser import parse
from openpulse.ast import (
    AngleType,
    CalibrationBlock,
    CalibrationDefinition,
    ClassicalArgument,
    ClassicalDeclaration,
    ComplexType,
    DurationType,
    ExternDeclaration,
    FloatType,
    FunctionCall,
    Identifier,
    IntegerLiteral,
    Program,
    PulseType,
    PulseTypeName,
    QASMNode,
    ReturnStatement,
    UnaryExpression,
    UnaryOperator,
)


class SpanGuard(QASMVisitor):
    """Ensure that we did not forget to set spans when we add new AST nodes"""

    def visit(self, node: QASMNode):
        try:
            assert node.span is not None
            return super().visit(node)
        except Exception as e:
            raise Exception(f"The span of {type(node)} is None.") from e


def test_calibration_definition():
    p = """
    defcal rz(angle[20] theta) $q{ return shift_phase(drive($q), -theta); }
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
                return_type=None,
                body=[
                    ReturnStatement(
                        expression=FunctionCall(
                            name=Identifier(name="shift_phase"),
                            arguments=[
                                FunctionCall(
                                    name=Identifier(name="drive"),
                                    arguments=[Identifier(name="$q")],
                                ),
                                UnaryExpression(
                                    op=UnaryOperator["-"], expression=Identifier(name="theta")
                                ),
                            ],
                        )
                    )
                ],
            )
        ]
    )
    SpanGuard().visit(program)


def test_calibration():
    p = """
    cal {
        extern drag(complex[float[size]], duration, duration, float[size]) -> waveform;

        port q0;

        frame q0_frame = newframe(q0, 0);
    }
    """.strip()
    program = parse(p)
    assert program == Program(
        statements=[
            CalibrationBlock(
                body=[
                    ExternDeclaration(
                        name="drag",
                        classical_types=[
                            ComplexType(
                                base_type=FloatType(Identifier("size")),
                            ),
                            DurationType(),
                            DurationType(),
                            FloatType(Identifier("size")),
                        ],
                        return_type=PulseType(type=PulseTypeName["waveform"]),
                    ),
                    ClassicalDeclaration(
                        type=PulseType(type=PulseTypeName["port"]),
                        identifier=Identifier(name="q0"),
                        init_expression=None,
                    ),
                    ClassicalDeclaration(
                        type=PulseType(type=PulseTypeName["frame"]),
                        identifier=Identifier(name="q0_frame"),
                        init_expression=FunctionCall(
                            name=Identifier(name="newframe"),
                            arguments=[Identifier(name="q0"), IntegerLiteral(value=0)],
                        ),
                    ),
                ]
            )
        ]
    )
    SpanGuard().visit(program)
