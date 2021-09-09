from openqasm.ast import (
    Identifier,
    QuantumGateModifier,
    QubitDeclaration,
    QuantumGate,
    QuantumGateDefinition,
)
from openqasm.ast_visitor.ast_visitor import NodeVisitor, NodeTransformer


class OpenNodePrinter(NodeVisitor):
    """
    Example visitor which "unparses" the Program back to text
    """

    def __init__(self):
        self.out = ""

    def _print(self, line):
        self.out += line
        self.out += "\n"

    def visit_QuantumGateDefinition(self, node: QuantumGateDefinition):
        self._print(f"gate {node.name} {', '.join(q.name for q in node.qubits)}" " {")
        for line in node.body:
            self.out += "    "
            self.visit(line)
        self._print("}\n")

    def visit_QubitDeclaration(self, node: QubitDeclaration):
        self._print(f"qubit {node.qubit.name};")

    def visit_QuantumGate(self, node: QuantumGate):
        for modifier in node.modifiers:
            self._print(f"{self.visit(modifier)} @ ")
        self._print(f"{node.name} {', '.join(q.name for q in node.qubits)};")

    def visit_QuantumGateModifier(self, node: QuantumGateModifier):
        self._print(node.modifier)
        if node.argument:
            self._print(f"({self.visit(node.argument)})")


class GateResolver(NodeTransformer):
    """
    Example transformer which inlines gate definitions to their call sites
    """

    def __init__(self):
        self.gate_defs = {}

    def visit_QuantumGateDefinition(self, node: QuantumGateDefinition):
        self.gate_defs[node.name] = node
        # returning None removes the node from the tree as desired
        return None

    def visit_QuantumGate(self, node: QuantumGate):
        gate_def = self.gate_defs[node.name]
        replacements = {old.name: new.name for old, new in zip(gate_def.qubits, node.qubits)}

        result = []
        for statement in gate_def.body:
            result.append(
                QuantumGate(
                    modifiers=statement.modifiers,
                    name=statement.name,
                    arguments=[],
                    qubits=[Identifier(replacements[old.name]) for old in statement.qubits],
                )
            )
        return result
