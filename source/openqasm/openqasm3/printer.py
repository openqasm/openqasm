import contextlib
import dataclasses
import io

from typing import Sequence, Optional

from . import ast, properties
from .visitor import QASMVisitor

__all__ = ("dump", "dumps")


def dump(node: ast.QASMNode, file: io.TextIOBase, **kwargs):
    _Printer(file, **kwargs).visit(node)


def dumps(node: ast.QASMNode, **kwargs):
    out = io.StringIO()
    dump(node, out, **kwargs)
    return out.getvalue()


@dataclasses.dataclass
class _PrinterState:
    """State object for the print visitor."""

    current_indent: int = 0
    skip_next_indent: bool = False

    @contextlib.contextmanager
    def increase_scope(self):
        self.current_indent += 1
        try:
            yield
        finally:
            self.current_indent -= 1


class _Printer(QASMVisitor[_PrinterState]):
    def __init__(
        self,
        stream: io.TextIOBase,
        *,
        indent: str = "  ",
        chain_else_if: bool = True,
        old_measurement: bool = False,
    ):
        """
        Args:
            stream (io.TextIOBase): the stream that the output will be written to.
            indent (str): the string to use as a single indentation level.
            chain_else_if (bool): If ``True``, then constructs of the form::

                    if (x == 0) {
                        // ...
                    } else {
                        if (x == 1) {
                            // ...
                        } else {
                            // ...
                        }
                    }

                will be collapsed into the equivalent but flatter::

                    if (x == 0) {
                        // ...
                    } else if (x == 1) {
                        // ...
                    } else {
                        // ...
                    }
            old_measurement (bool): If ``True``, then the OpenQASM 2-style "arrow" measurements will
                be used instead of the normal assignments.  For example, ``old_measurement=False``
                (the default) will emit ``a = measure b;`` where ``old_measurement=True`` would emit
                ``measure b -> a;`` instead.
        """
        self.stream = stream
        self.indent = indent
        self.chain_else_if = chain_else_if
        self.old_measurement = old_measurement

    def visit(self, node: ast.QASMNode, context: Optional[_PrinterState] = None) -> None:
        if context is None:
            context = _PrinterState()
        return super().visit(node, context)

    def _start_line(self, context: _PrinterState) -> None:
        if context.skip_next_indent:
            context.skip_next_indent = False
            return
        self.stream.write(context.current_indent * self.indent)

    def _end_statement(self, context: _PrinterState) -> None:
        self.stream.write(";\n")

    def _end_line(self, context: _PrinterState) -> None:
        self.stream.write("\n")

    def _write_statement(self, line: str, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write(line)
        self._end_statement(context)

    def _visit_sequence(
        self,
        nodes: Sequence[ast.QASMNode],
        context: _PrinterState,
        *,
        start: str = "",
        end: str = "",
        separator: str,
    ) -> None:
        if start:
            self.stream.write(start)
        for node in nodes[:-1]:
            self.visit(node, context)
            self.stream.write(separator)
        if nodes:
            self.visit(nodes[-1], context)
        if end:
            self.stream.write(end)

    def visit_Program(self, node: ast.Program, context: _PrinterState) -> None:
        if node.version:
            self._write_statement(f"OPENQASM {node.version}", context)
        for include in node.includes:
            self.visit(include, context)
        for io_declaration in node.io_variables:
            self.visit(io_declaration, context)
        for statement in node.statements:
            self.visit(statement, context)

    def visit_Include(self, node: ast.Include, context: _PrinterState) -> None:
        self._write_statement(f'include "{node.filename}"', context)

    def visit_ExpressionStatement(
        self, node: ast.ExpressionStatement, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.expression, context)
        self._end_statement(context)

    def visit_QubitDeclaration(self, node: ast.QubitDeclaration, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("qubit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size)
            self.stream.write("]")
        self.stream.write(" ")
        self.visit(node.qubit, context)
        self._end_statement(context)

    def visit_QuantumGateDefinition(
        self, node: ast.QuantumGateDefinition, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("gate ")
        self.visit(node.name, context)
        if node.arguments:
            self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        self.stream.write(" ")
        self._visit_sequence(node.qubits, context, separator=", ")
        self.stream.write(" {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.body:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_ExternDeclaration(self, node: ast.ExternDeclaration, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("extern ")
        self.visit(node.name, context)
        self._visit_sequence(node.classical_types, context, start="(", end=")", separator=", ")
        if node.return_type is not None:
            self.stream.write(" -> ")
            self.visit(node.return_type, context)
        self._end_statement(context)

    def visit_Identifier(self, node: ast.Identifier, context: _PrinterState) -> None:
        self.stream.write(node.name)

    def visit_UnaryExpression(self, node: ast.UnaryExpression, context: _PrinterState) -> None:
        self.stream.write(node.op.name)
        if properties.precedence(node) >= properties.precedence(node.expression):
            self.stream.write("(")
            self.visit(node.expression, context)
            self.stream.write(")")
        else:
            self.visit(node.expression, context)

    def visit_BinaryExpression(self, node: ast.BinaryExpression, context: _PrinterState) -> None:
        our_precedence = properties.precedence(node)
        # All AST nodes that are built into BinaryExpression are currently left associative.
        if properties.precedence(node.lhs) < our_precedence:
            self.stream.write("(")
            self.visit(node.lhs, context)
            self.stream.write(")")
        else:
            self.visit(node.lhs, context)
        self.stream.write(f" {node.op.name} ")
        if properties.precedence(node.rhs) <= our_precedence:
            self.stream.write("(")
            self.visit(node.rhs, context)
            self.stream.write(")")
        else:
            self.visit(node.rhs, context)

    def visit_Constant(self, node: ast.Constant, context: _PrinterState) -> None:
        self.stream.write(node.name.name)

    def visit_BitstringLiteral(self, node: ast.BitstringLiteral, context: _PrinterState) -> None:
        value = bin(node.value)[2:]
        if len(value) < node.width:
            value = "0" * (node.width - len(value)) + value
        self.stream.write(f'"{value}"')

    def visit_IntegerLiteral(self, node: ast.IntegerLiteral, context: _PrinterState) -> None:
        self.stream.write(str(node.value))

    def visit_FloatLiteral(self, node: ast.FloatLiteral, context: _PrinterState) -> None:
        self.stream.write(str(node.value))

    def visit_BooleanLiteral(self, node: ast.BooleanLiteral, context: _PrinterState) -> None:
        self.stream.write("true" if node.value else "false")

    def visit_StringLiteral(self, node: ast.StringLiteral, context: _PrinterState) -> None:
        self.stream.write(f'"{node.value}"')

    def visit_DurationLiteral(self, node: ast.DurationLiteral, context: _PrinterState) -> None:
        self.stream.write(f"{node.value}{node.unit.name}")

    def visit_ArrayLiteral(self, node: ast.ArrayLiteral, context: _PrinterState) -> None:
        self._visit_sequence(node.values, context, start="{", end="}", separator=", ")

    def visit_FunctionCall(self, node: ast.FunctionCall, context: _PrinterState) -> None:
        self.visit(node.name)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")

    def visit_Cast(self, node: ast.Cast, context: _PrinterState) -> None:
        self.visit(node.type)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")

    def visit_DiscreteSet(self, node: ast.DiscreteSet, context: _PrinterState) -> None:
        self._visit_sequence(node.values, context, start="{", end="}", separator=", ")

    def visit_RangeDefinition(self, node: ast.RangeDefinition, context: _PrinterState) -> None:
        if node.start is not None:
            self.visit(node.start, context)
        self.stream.write(":")
        if node.step is not None:
            self.visit(node.step, context)
            self.stream.write(":")
        if node.end is not None:
            self.visit(node.end, context)

    def visit_IndexExpression(self, node: ast.IndexExpression, context: _PrinterState) -> None:
        if properties.precedence(node.collection) < properties.precedence(node):
            self.stream.write("(")
            self.visit(node.collection, context)
            self.stream.write(")")
        else:
            self.visit(node.collection, context)
        self.stream.write("[")
        if isinstance(node.index, ast.DiscreteSet):
            self.visit(node.index, context)
        else:
            self._visit_sequence(node.index, context, separator=", ")
        self.stream.write("]")

    def visit_IndexedIdentifier(self, node: ast.IndexedIdentifier, context: _PrinterState) -> None:
        self.visit(node.name, context)
        for index in node.indices:
            self.stream.write("[")
            if isinstance(index, ast.DiscreteSet):
                self.visit(index, context)
            else:
                self._visit_sequence(index, context, separator=", ")
            self.stream.write("]")

    def visit_Concatenation(self, node: ast.Concatenation, context: _PrinterState) -> None:
        lhs_precedence = properties.precedence(node.lhs)
        our_precedence = properties.precedence(node)
        rhs_precedence = properties.precedence(node.rhs)
        # Concatenation is fully associative, but this package parses the AST by
        # arbitrarily making it left-associative (since the design of the AST
        # forces us to make a choice).  We emit brackets to ensure that the
        # round-trip through our printer and parser do not change the AST.
        if lhs_precedence < our_precedence:
            self.stream.write("(")
            self.visit(node.lhs, context)
            self.stream.write(")")
        else:
            self.visit(node.lhs, context)
        self.stream.write(" ++ ")
        if rhs_precedence <= our_precedence:
            self.stream.write("(")
            self.visit(node.rhs, context)
            self.stream.write(")")
        else:
            self.visit(node.rhs, context)

    def visit_QuantumGate(self, node: ast.QuantumGate, context: _PrinterState) -> None:
        self._start_line(context)
        if node.modifiers:
            self._visit_sequence(node.modifiers, context, end=" @ ", separator=" @ ")
        self.visit(node.name, context)
        if node.arguments:
            self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        self.stream.write(" ")
        self._visit_sequence(node.qubits, context, separator=", ")
        self._end_statement(context)

    def visit_QuantumGateModifier(
        self, node: ast.QuantumGateModifier, context: _PrinterState
    ) -> None:
        self.stream.write(node.modifier.name)
        if node.argument is not None:
            self.stream.write("(")
            self.visit(node.argument, context)
            self.stream.write(")")

    def visit_QuantumPhase(self, node: ast.QuantumPhase, context: _PrinterState) -> None:
        self._start_line(context)
        if node.quantum_gate_modifiers:
            self._visit_sequence(node.quantum_gate_modifiers, context, end=" @ ", separator=" @ ")
        self.stream.write("gphase(")
        self.visit(node.argument, context)
        self.stream.write(")")
        if node.qubits:
            self._visit_sequence(node.qubits, context, start=" ", separator=", ")
        self._end_statement(context)

    def visit_QuantumMeasurement(
        self, node: ast.QuantumMeasurement, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("measure ")
        self.visit(node.qubit, context)
        self._end_statement(context)

    def visit_QuantumReset(self, node: ast.QuantumReset, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("reset ")
        self.visit(node.qubits, context)
        self._end_statement(context)

    def visit_QuantumBarrier(self, node: ast.QuantumBarrier, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("barrier ")
        self._visit_sequence(node.qubits, context, separator=", ")
        self._end_statement(context)

    def visit_QuantumMeasurementAssignment(
        self, node: ast.QuantumMeasurementAssignment, context: _PrinterState
    ) -> None:
        if node.target is None:
            # If we're here, this node has matched in the context of being the
            # rhs of some assignment to a variable.
            self.stream.write("measure ")
            self.visit(node.measure_instruction.qubit, context)
            self._end_statement(context)
            return
        self._start_line(context)
        if self.old_measurement:
            self.stream.write("measure ")
            self.visit(node.measure_instruction.qubit, context)
            self.stream.write(" -> ")
            self.visit(node.target, context)
        else:
            self.visit(node.target, context)
            self.stream.write(" = measure ")
            self.visit(node.measure_instruction.qubit, context)
        self._end_statement(context)

    def visit_ClassicalArgument(self, node: ast.ClassicalArgument, context: _PrinterState) -> None:
        if node.access is not None:
            self.stream.write("const " if node.access == ast.AccessControl.CONST else "mutable ")
        self.visit(node.type, context)
        self.stream.write(" ")
        self.visit(node.name, context)

    def visit_ClassicalDeclaration(
        self, node: ast.ClassicalDeclaration, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.type)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        if node.init_expression is not None:
            self.stream.write(" = ")
            self.visit(node.init_expression)
        self._end_statement(context)

    def visit_IODeclaration(self, node: ast.IODeclaration, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write(f"{node.io_identifier.name} ")
        self.visit(node.type)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        if node.init_expression is not None:
            self.stream.write(" = ")
            self.visit(node.init_expression)
        self._end_statement(context)

    def visit_ConstantDeclaration(
        self, node: ast.ConstantDeclaration, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("const ")
        self.visit(node.type, context)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        self.stream.write(" = ")
        self.visit(node.init_expression, context)
        self._end_statement(context)

    def visit_IntType(self, node: ast.IntType, context: _PrinterState) -> None:
        self.stream.write("int")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_UintType(self, node: ast.UintType, context: _PrinterState) -> None:
        self.stream.write("uint")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_FloatType(self, node: ast.FloatType, context: _PrinterState) -> None:
        self.stream.write("float")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_ComplexType(self, node: ast.ComplexType, context: _PrinterState) -> None:
        self.stream.write("complex[")
        self.visit(node.base_type, context)
        self.stream.write("]")

    def visit_AngleType(self, node: ast.AngleType, context: _PrinterState) -> None:
        self.stream.write("angle")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_BitType(self, node: ast.BitType, context: _PrinterState) -> None:
        self.stream.write("bit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_BoolType(self, node: ast.BoolType, context: _PrinterState) -> None:
        self.stream.write("bool")

    def visit_ArrayType(self, node: ast.ArrayType, context: _PrinterState) -> None:
        self.stream.write("array[")
        self.visit(node.base_type, context)
        self._visit_sequence(node.dimensions, context, start=", ", end="]", separator=", ")

    def visit_ArrayReferenceType(
        self, node: ast.ArrayReferenceType, context: _PrinterState
    ) -> None:
        self.stream.write("array[")
        self.visit(node.base_type, context)
        self.stream.write(", ")
        if isinstance(node.dimensions, ast.Expression):
            self.stream.write("#dim=")
            self.visit(node.dimensions, context)
        else:
            self._visit_sequence(node.dimensions, context, separator=", ")
        self.stream.write("]")

    def visit_DurationType(self, node: ast.DurationType, context: _PrinterState) -> None:
        self.stream.write("duration")

    def visit_StretchType(self, node: ast.StretchType, context: _PrinterState) -> None:
        self.stream.write("stretch")

    def visit_CalibrationGrammarDeclaration(
        self, node: ast.CalibrationGrammarDeclaration, context: _PrinterState
    ) -> None:
        self._write_statement(f'defcalgrammar "{node.calibration_grammar}"', context)

    def visit_CalibrationDefinition(
        self, node: ast.CalibrationDefinition, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("defcal ")
        self.visit(node.name, context)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        self.stream.write(" ")
        self._visit_sequence(node.qubits, context, separator=", ")
        if node.return_type is not None:
            self.stream.write(" -> ")
            self.visit(node.return_type, context)
        self.stream.write(" {")
        # At this point we _should_ be deferring to something else to handle formatting the
        # calibration grammar statements, but we're neither we nor the AST are set up to do that.
        self.stream.write(node.body)
        self.stream.write("}")
        self._end_line(context)

    def visit_SubroutineDefinition(
        self, node: ast.SubroutineDefinition, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("def ")
        self.visit(node.name, context)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        if node.return_type is not None:
            self.stream.write(" -> ")
            self.visit(node.return_type, context)
        self.stream.write(" {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.body:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_QuantumArgument(self, node: ast.QuantumArgument, context: _PrinterState) -> None:
        self.stream.write("qubit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")
        self.stream.write(" ")
        self.visit(node.qubit, context)

    def visit_ReturnStatement(self, node: ast.ReturnStatement, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("return")
        if node.expression is not None:
            self.stream.write(" ")
            if isinstance(node.expression, ast.QuantumMeasurement):
                # Handle this specially, since in most cases it's a statement.
                self.stream.write("measure ")
                self.visit(node.expression.qubit, context)
            else:
                self.visit(node.expression)
        self._end_statement(context)

    def visit_BreakStatement(self, node: ast.BreakStatement, context: _PrinterState) -> None:
        self._write_statement("break", context)

    def visit_ContinueStatement(self, node: ast.ContinueStatement, context: _PrinterState) -> None:
        self._write_statement("continue", context)

    def visit_EndStatement(self, node: ast.EndStatement, context: _PrinterState) -> None:
        self._write_statement("end", context)

    def visit_BranchingStatement(
        self, node: ast.BranchingStatement, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("if (")
        self.visit(node.condition, context)
        self.stream.write(") {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.if_block:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        if node.else_block:
            self.stream.write(" else ")
            # Special handling to flatten a perfectly nested structure of
            #   if {...} else { if {...} else {...} }
            # into the simpler
            #   if {...} else if {...} else {...}
            # but only if we're allowed to by our options.
            if (
                self.chain_else_if
                and len(node.else_block) == 1
                and isinstance(node.else_block[0], ast.BranchingStatement)
            ):
                context.skip_next_indent = True
                self.visit(node.else_block[0], context)
                # Don't end the line, because the outer-most `if` block will.
            else:
                self.stream.write("{")
                self._end_line(context)
                with context.increase_scope():
                    for statement in node.else_block:
                        self.visit(statement, context)
                self._start_line(context)
                self.stream.write("}")
                self._end_line(context)
        else:
            self._end_line(context)

    def visit_WhileLoop(self, node: ast.WhileLoop, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("while (")
        self.visit(node.while_condition, context)
        self.stream.write(") {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.block:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_ForInLoop(self, node: ast.ForInLoop, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("for ")
        self.visit(node.loop_variable, context)
        self.stream.write(" in ")
        if isinstance(node.set_declaration, ast.RangeDefinition):
            self.stream.write("[")
            self.visit(node.set_declaration, context)
            self.stream.write("]")
        else:
            self.visit(node.set_declaration, context)
        self.stream.write(" {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.block:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_DelayInstruction(self, node: ast.DelayInstruction, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("delay[")
        self.visit(node.duration, context)
        self.stream.write("] ")
        self._visit_sequence(node.qubits, context, separator=", ")
        self._end_statement(context)

    def visit_Box(self, node: ast.Box, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("box")
        if node.duration is not None:
            self.stream.write("[")
            self.visit(node.duration, context)
            self.stream.write("]")
        self.stream.write(" {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.body:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_DurationOf(self, node: ast.DurationOf, context: _PrinterState) -> None:
        self.stream.write("durationof(")
        if isinstance(node.target, ast.QASMNode):
            self.visit(node.target, context)
        else:
            self.stream.write("{")
            self._end_line(context)
            with context.increase_scope():
                for statement in node.target:
                    self.visit(statement, context)
            self._start_line(context)
            self.stream.write("}")
        self.stream.write(")")

    def visit_AliasStatement(self, node: ast.AliasStatement, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("let ")
        self.visit(node.target, context)
        self.stream.write(" = ")
        self.visit(node.value, context)
        self._end_statement(context)

    def visit_ClassicalAssignment(
        self, node: ast.ClassicalAssignment, context: _PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.lvalue, context)
        self.stream.write(f" {node.op.name} ")
        self.visit(node.rvalue, context)
        self._end_statement(context)

    def visit_Pragma(self, node: ast.Pragma, context: _PrinterState) -> None:
        self._start_line(context)
        self.stream.write("#pragma {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.statements:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)
