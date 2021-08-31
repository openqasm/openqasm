from open_node.ast import OpenNode
from open_node.parser.antlr.qasm_parser import parse
from open_node.ast_visitor.ast_visitor_examples import OpenNodePrinter, GateResolver


def unparse(program: OpenNode):
    printer = OpenNodePrinter()
    printer.visit(program)
    return printer.out.strip()


def test_printer():
    p = """
gate xyz q {
    x q;
    y q;
    z q;
}

qubit q;
qubit r;
h q;
cx q, r;
""".strip()

    assert p == unparse(parse(p))


def test_gate_resolver():
    old = """
gate xyz q {
    x q;
    y q;
    z q;
}

qubit q;
qubit r;
xyz q;
xyz r;
""".strip()

    new = """
qubit q;
qubit r;
x q;
y q;
z q;
x r;
y r;
z r;
""".strip()

    transformed = GateResolver().visit(parse(old))
    assert new == unparse(transformed)
