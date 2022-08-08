import dataclasses

from openqasm3.visitor import QASMVisitor

from openpulse.parser import parse
from openpulse.ast import (
    AngleType,
    CalibrationDefinition,
    CalibrationStatement,
    ClassicalArgument,
    ClassicalDeclaration,
    ComplexType,
    DurationType,
    ExternArgument,
    ExternDeclaration,
    FloatType,
    FunctionCall,
    Identifier,
    IntegerLiteral,
    Program,
    QASMNode,
    ReturnStatement,
    UnaryExpression,
    UnaryOperator,
    FrameType,
    PortType,
    WaveformType,
)


class SpanGuard(QASMVisitor):
    """Ensure that we did not forget to set spans when we add new AST nodes"""

    def visit(self, node: QASMNode):
        try:
            assert node.span is not None
            return super().visit(node)
        except Exception as e:
            raise Exception(f"The span of {type(node)} is None.") from e


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


def test_calibration_definition():
    p = """
    defcal rz(angle[20] theta) $1 { return shift_phase(drive($1), -theta); }
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
                qubits=[Identifier("$1")],
                return_type=None,
                body=[
                    ReturnStatement(
                        expression=FunctionCall(
                            name=Identifier(name="shift_phase"),
                            arguments=[
                                FunctionCall(
                                    name=Identifier(name="drive"),
                                    arguments=[Identifier(name="$1")],
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
    assert _remove_spans(program) == Program(
        statements=[
            CalibrationStatement(
                body=[
                    ExternDeclaration(
                        name=Identifier("drag"),
                        arguments=[
                            ExternArgument(
                                type=ComplexType(
                                    base_type=FloatType(size=Identifier("size")),
                                )
                            ),
                            ExternArgument(type=DurationType()),
                            ExternArgument(type=DurationType()),
                            ExternArgument(type=FloatType(Identifier("size"))),
                        ],
                        return_type=WaveformType(),
                    ),
                    ClassicalDeclaration(
                        type=PortType(),
                        identifier=Identifier(name="q0"),
                        init_expression=None,
                    ),
                    ClassicalDeclaration(
                        type=FrameType(),
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
