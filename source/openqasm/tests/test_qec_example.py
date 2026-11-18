"""Regression coverage for the repetition-code example's syndrome corrections."""

from pathlib import Path

import openqasm3
from openqasm3 import ast

EXAMPLE = Path(__file__).resolve().parents[3] / "examples" / "qec.qasm"


def test_qec_syndrome_corrections_use_unsigned_two_bit_values():
    program = openqasm3.parse(EXAMPLE.read_text())
    corrections = [
        statement
        for statement in program.statements
        if isinstance(statement, ast.BranchingStatement)
    ]
    assert len(corrections) == 3

    for correction, (syndrome, qubit) in zip(corrections, ((1, 0), (2, 2), (3, 1))):
        condition = correction.condition
        assert isinstance(condition, ast.BinaryExpression)
        assert condition.op == ast.BinaryOperator["=="]
        assert isinstance(condition.lhs, ast.Cast)
        assert condition.lhs.type == ast.UintType(ast.IntegerLiteral(2))
        assert condition.lhs.argument == ast.Identifier("syn")
        assert condition.rhs == ast.IntegerLiteral(syndrome)
        assert len(correction.if_block) == 1
        gate = correction.if_block[0]
        assert isinstance(gate, ast.QuantumGate)
        assert gate.name == ast.Identifier("x")
        assert gate.qubits == [
            ast.IndexedIdentifier(ast.Identifier("q"), [[ast.IntegerLiteral(qubit)]])
        ]
