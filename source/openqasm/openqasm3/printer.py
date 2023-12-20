"""
==============================================================
Generating OpenQASM 3 from an AST Node (``openqasm3.printer``)
==============================================================

.. currentmodule:: openqasm3

It is often useful to go from the :mod:`AST representation <openqasm3.ast>` of an OpenQASM 3 program
back to the textual language.  The functions and classes described here will do this conversion.

Most uses should be covered by using :func:`dump` to write to an open text stream (an open file, for
example) or :func:`dumps` to produce a string.  Both of these accept :ref:`several keyword arguments
<printer-kwargs>` that control the formatting of the output.

.. autofunction:: openqasm3.dump
.. autofunction:: openqasm3.dumps


.. _printer-kwargs:

Controlling the formatting
==========================

.. currentmodule:: openqasm3.printer

The :func:`~openqasm3.dump` and :func:`~openqasm3.dumps` functions both use an internal AST-visitor
class to operate on the AST.  This class actually defines all the formatting options, and can be
used for more low-level operations, such as writing a program piece-by-piece.  This may need access
to the :ref:`printer state <printer-state>`, documented below.

.. autoclass:: Printer
    :members:
    :class-doc-from: both

For the most complete control, it is possible to subclass this printer and override only the visitor
methods that should be modified.


.. _printer-state:

Reusing the same printer
========================

.. currentmodule:: openqasm3.printer

If the :class:`Printer` is being reused to write multiple nodes to a single stream, you will also
likely need to access its internal state.  This can be done by manually creating a
:class:`PrinterState` object and passing it in the original call to :meth:`Printer.visit`.  The
state object is mutated by the visit, and will reflect the output state at the end.

.. autoclass:: PrinterState
    :members:
"""


import contextlib
import dataclasses
import io
import functools

from typing import List, Optional, Sequence

from . import ast, properties
from .visitor import QASMVisitor

__all__ = ("dump", "dumps", "Printer", "PrinterState")


def dump(node: ast.QASMNode, file: io.TextIOBase, **kwargs) -> None:
    """Write textual OpenQASM 3 code representing ``node`` to the open stream ``file``.

    It is generally expected that ``node`` will be an instance of :class:`.ast.Program`, but this
    does not need to be the case.

    For more details on the available keyword arguments, see :ref:`printer-kwargs`.
    """
    Printer(file, **kwargs).visit(node)


def dumps(node: ast.QASMNode, **kwargs) -> str:
    """Get a string representation of the OpenQASM 3 code representing ``node``.

    It is generally expected that ``node`` will be an instance of :class:`.ast.Program`, but this
    does not need to be the case.

    For more details on the available keyword arguments, see :ref:`printer-kwargs`.
    """
    out = io.StringIO()
    dump(node, out, **kwargs)
    return out.getvalue()


@dataclasses.dataclass
class PrinterState:
    """State object for the print visitor.  This is mutated during the visit."""

    current_indent: int = 0
    """The current indentation level.  This is a non-negative integer; the actual identation string
    to be used is defined by the :class:`Printer`."""
    skip_next_indent: bool = False
    """This is used to communicate between the different levels of if-else visitors when emitting
    chained ``else if`` blocks.  The chaining occurs with the next ``if`` if this is set to
    ``True``."""

    @contextlib.contextmanager
    def increase_scope(self):
        """Use as a context manager to increase the scoping level of this context inside the
        resource block."""
        self.current_indent += 1
        try:
            yield
        finally:
            self.current_indent -= 1


def _maybe_annotated(method):
    @functools.wraps(method)
    def annotated(self: "Printer", node: ast.Statement, context: PrinterState) -> None:
        for annotation in node.annotations:
            self.visit(annotation, context)
        return method(self, node, context)

    return annotated


class Printer(QASMVisitor[PrinterState]):
    """Internal AST-visitor for writing AST nodes out to a stream as valid OpenQASM 3.

    This class can be used directly to write multiple nodes to the same stream, potentially with
    some manual control fo the state between them.

    If subclassing, generally only the specialised ``visit_*`` methods need to be overridden.  These
    are derived from the base class, and use the name of the relevant :mod:`AST node <.ast>`
    verbatim after ``visit_``."""

    def __init__(
        self,
        stream: io.TextIOBase,
        *,
        indent: str = "  ",
        chain_else_if: bool = True,
        old_measurement: bool = False,
    ):
        """
        Aside from ``stream``, the arguments here are keyword arguments that are common to this
        class, :func:`~openqasm3.dump` and :func:`~openqasm3.dumps`.

        :param stream: the stream that the output will be written to.
        :type stream: io.TextIOBase

        :param indent: the string to use as a single indentation level.
        :type indent: str, optional (two spaces).

        :param chain_else_if:  If ``True`` (default), then constructs of the form::

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

        :type chain_else_if: bool, optional (``True``)

        :param old_measurement: If ``True``, then the OpenQASM 2-style "arrow" measurements will be
            used instead of the normal assignments.  For example, ``old_measurement=False`` (the
            default) will emit ``a = measure b;`` where ``old_measurement=True`` would emit
            ``measure b -> a;`` instead.
        :type old_measurement: bool, optional (``False``).
        """
        self.stream = stream
        self.indent = indent
        self.chain_else_if = chain_else_if
        self.old_measurement = old_measurement

    def visit(self, node: ast.QASMNode, context: Optional[PrinterState] = None) -> None:
        """Completely visit a node and all subnodes.  This is the dispatch entry point; this will
        automatically result in the correct specialised visitor getting called.

        :param node: The AST node to visit.  Usually this will be an :class:`.ast.Program`.
        :type node: .ast.QASMNode

        :param context: The state object to be used during the visit.  If not given, a default
            object will be constructed and used.
        :type context: PrinterState
        """
        if context is None:
            context = PrinterState()
        return super().visit(node, context)

    def _start_line(self, context: PrinterState) -> None:
        if context.skip_next_indent:
            context.skip_next_indent = False
            return
        self.stream.write(context.current_indent * self.indent)

    def _end_statement(self, context: PrinterState) -> None:
        self.stream.write(";\n")

    def _end_line(self, context: PrinterState) -> None:
        self.stream.write("\n")

    def _write_statement(self, line: str, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write(line)
        self._end_statement(context)

    def _visit_statement_list(
        self, nodes: List[ast.Statement], context: PrinterState, prefix: str = ""
    ) -> None:
        self.stream.write(prefix)
        self.stream.write("{")
        self._end_line(context)
        with context.increase_scope():
            for statement in nodes:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")

    def _visit_sequence(
        self,
        nodes: Sequence[ast.QASMNode],
        context: PrinterState,
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

    def visit_Program(self, node: ast.Program, context: PrinterState) -> None:
        if node.version:
            self._write_statement(f"OPENQASM {node.version}", context)
        for statement in node.statements:
            self.visit(statement, context)

    @_maybe_annotated
    def visit_CompoundStatement(self, node: ast.CompoundStatement, context: PrinterState) -> None:
        self._start_line(context)
        self._visit_statement_list(node.statements, context)
        self._end_line(context)

    @_maybe_annotated
    def visit_Include(self, node: ast.Include, context: PrinterState) -> None:
        self._write_statement(f'include "{node.filename}"', context)

    @_maybe_annotated
    def visit_ExpressionStatement(
        self, node: ast.ExpressionStatement, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.expression, context)
        self._end_statement(context)

    @_maybe_annotated
    def visit_QubitDeclaration(self, node: ast.QubitDeclaration, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("qubit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size)
            self.stream.write("]")
        self.stream.write(" ")
        self.visit(node.qubit, context)
        self._end_statement(context)

    @_maybe_annotated
    def visit_QuantumGateDefinition(
        self, node: ast.QuantumGateDefinition, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("gate ")
        self.visit(node.name, context)
        if node.arguments:
            self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        self.stream.write(" ")
        self._visit_sequence(node.qubits, context, separator=", ")
        self._visit_statement_list(node.body, context, prefix=" ")
        self._end_line(context)

    @_maybe_annotated
    def visit_ExternDeclaration(self, node: ast.ExternDeclaration, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("extern ")
        self.visit(node.name, context)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        if node.return_type is not None:
            self.stream.write(" -> ")
            self.visit(node.return_type, context)
        self._end_statement(context)

    def visit_Identifier(self, node: ast.Identifier, context: PrinterState) -> None:
        self.stream.write(node.name)

    def visit_UnaryExpression(self, node: ast.UnaryExpression, context: PrinterState) -> None:
        self.stream.write(node.op.name)
        if properties.precedence(node) >= properties.precedence(node.expression):
            self.stream.write("(")
            self.visit(node.expression, context)
            self.stream.write(")")
        else:
            self.visit(node.expression, context)

    def visit_BinaryExpression(self, node: ast.BinaryExpression, context: PrinterState) -> None:
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

    def visit_BitstringLiteral(self, node: ast.BitstringLiteral, context: PrinterState) -> None:
        value = bin(node.value)[2:]
        if len(value) < node.width:
            value = "0" * (node.width - len(value)) + value
        self.stream.write(f'"{value}"')

    def visit_IntegerLiteral(self, node: ast.IntegerLiteral, context: PrinterState) -> None:
        self.stream.write(str(node.value))

    def visit_FloatLiteral(self, node: ast.FloatLiteral, context: PrinterState) -> None:
        self.stream.write(str(node.value))

    def visit_ImaginaryLiteral(self, node: ast.ImaginaryLiteral, context: PrinterState) -> None:
        self.stream.write(str(node.value) + "im")

    def visit_BooleanLiteral(self, node: ast.BooleanLiteral, context: PrinterState) -> None:
        self.stream.write("true" if node.value else "false")

    def visit_DurationLiteral(self, node: ast.DurationLiteral, context: PrinterState) -> None:
        self.stream.write(f"{node.value}{node.unit.name}")

    def visit_ArrayLiteral(self, node: ast.ArrayLiteral, context: PrinterState) -> None:
        self._visit_sequence(node.values, context, start="{", end="}", separator=", ")

    def visit_FunctionCall(self, node: ast.FunctionCall, context: PrinterState) -> None:
        self.visit(node.name)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")

    def visit_Cast(self, node: ast.Cast, context: PrinterState) -> None:
        self.visit(node.type)
        self.stream.write("(")
        self.visit(node.argument)
        self.stream.write(")")

    def visit_DiscreteSet(self, node: ast.DiscreteSet, context: PrinterState) -> None:
        self._visit_sequence(node.values, context, start="{", end="}", separator=", ")

    def visit_RangeDefinition(self, node: ast.RangeDefinition, context: PrinterState) -> None:
        if node.start is not None:
            self.visit(node.start, context)
        self.stream.write(":")
        if node.step is not None:
            self.visit(node.step, context)
            self.stream.write(":")
        if node.end is not None:
            self.visit(node.end, context)

    def visit_IndexExpression(self, node: ast.IndexExpression, context: PrinterState) -> None:
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

    def visit_IndexedIdentifier(self, node: ast.IndexedIdentifier, context: PrinterState) -> None:
        self.visit(node.name, context)
        for index in node.indices:
            self.stream.write("[")
            if isinstance(index, ast.DiscreteSet):
                self.visit(index, context)
            else:
                self._visit_sequence(index, context, separator=", ")
            self.stream.write("]")

    def visit_Concatenation(self, node: ast.Concatenation, context: PrinterState) -> None:
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

    @_maybe_annotated
    def visit_QuantumGate(self, node: ast.QuantumGate, context: PrinterState) -> None:
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
        self, node: ast.QuantumGateModifier, context: PrinterState
    ) -> None:
        self.stream.write(node.modifier.name)
        if node.argument is not None:
            self.stream.write("(")
            self.visit(node.argument, context)
            self.stream.write(")")

    @_maybe_annotated
    def visit_QuantumPhase(self, node: ast.QuantumPhase, context: PrinterState) -> None:
        self._start_line(context)
        if node.modifiers:
            self._visit_sequence(node.modifiers, context, end=" @ ", separator=" @ ")
        self.stream.write("gphase(")
        self.visit(node.argument, context)
        self.stream.write(")")
        if node.qubits:
            self._visit_sequence(node.qubits, context, start=" ", separator=", ")
        self._end_statement(context)

    def visit_QuantumMeasurement(self, node: ast.QuantumMeasurement, context: PrinterState) -> None:
        self.stream.write("measure ")
        self.visit(node.qubit, context)

    @_maybe_annotated
    def visit_QuantumReset(self, node: ast.QuantumReset, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("reset ")
        self.visit(node.qubits, context)
        self._end_statement(context)

    @_maybe_annotated
    def visit_QuantumBarrier(self, node: ast.QuantumBarrier, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("barrier")
        if node.qubits:
            self.stream.write(" ")
            self._visit_sequence(node.qubits, context, separator=", ")
        self._end_statement(context)

    @_maybe_annotated
    def visit_QuantumMeasurementStatement(
        self, node: ast.QuantumMeasurementStatement, context: PrinterState
    ) -> None:
        self._start_line(context)
        if node.target is None:
            self.visit(node.measure, context)
        elif self.old_measurement:
            self.visit(node.measure, context)
            self.stream.write(" -> ")
            self.visit(node.target, context)
        else:
            self.visit(node.target, context)
            self.stream.write(" = ")
            self.visit(node.measure, context)
        self._end_statement(context)

    def visit_ClassicalArgument(self, node: ast.ClassicalArgument, context: PrinterState) -> None:
        if node.access is not None:
            self.stream.write(
                "readonly " if node.access == ast.AccessControl.readonly else "mutable "
            )
        self.visit(node.type, context)
        self.stream.write(" ")
        self.visit(node.name, context)

    def visit_ExternArgument(self, node: ast.ExternArgument, context: PrinterState) -> None:
        if node.access is not None:
            self.stream.write(
                "readonly " if node.access == ast.AccessControl.readonly else "mutable "
            )
        self.visit(node.type, context)

    @_maybe_annotated
    def visit_ClassicalDeclaration(
        self, node: ast.ClassicalDeclaration, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.type)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        if node.init_expression is not None:
            self.stream.write(" = ")
            self.visit(node.init_expression)
        self._end_statement(context)

    @_maybe_annotated
    def visit_IODeclaration(self, node: ast.IODeclaration, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write(f"{node.io_identifier.name} ")
        self.visit(node.type)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        self._end_statement(context)

    @_maybe_annotated
    def visit_ConstantDeclaration(
        self, node: ast.ConstantDeclaration, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("const ")
        self.visit(node.type, context)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        self.stream.write(" = ")
        self.visit(node.init_expression, context)
        self._end_statement(context)

    def visit_IntType(self, node: ast.IntType, context: PrinterState) -> None:
        self.stream.write("int")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_UintType(self, node: ast.UintType, context: PrinterState) -> None:
        self.stream.write("uint")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_FloatType(self, node: ast.FloatType, context: PrinterState) -> None:
        self.stream.write("float")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_ComplexType(self, node: ast.ComplexType, context: PrinterState) -> None:
        self.stream.write("complex")
        if node.base_type is not None:
            self.stream.write("[")
            self.visit(node.base_type, context)
            self.stream.write("]")

    def visit_AngleType(self, node: ast.AngleType, context: PrinterState) -> None:
        self.stream.write("angle")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_BitType(self, node: ast.BitType, context: PrinterState) -> None:
        self.stream.write("bit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")

    def visit_BoolType(self, node: ast.BoolType, context: PrinterState) -> None:
        self.stream.write("bool")

    def visit_ArrayType(self, node: ast.ArrayType, context: PrinterState) -> None:
        self.stream.write("array[")
        self.visit(node.base_type, context)
        self._visit_sequence(node.dimensions, context, start=", ", end="]", separator=", ")

    def visit_ArrayReferenceType(self, node: ast.ArrayReferenceType, context: PrinterState) -> None:
        self.stream.write("array[")
        self.visit(node.base_type, context)
        self.stream.write(", ")
        if isinstance(node.dimensions, ast.Expression):
            self.stream.write("#dim=")
            self.visit(node.dimensions, context)
        else:
            self._visit_sequence(node.dimensions, context, separator=", ")
        self.stream.write("]")

    def visit_DurationType(self, node: ast.DurationType, context: PrinterState) -> None:
        self.stream.write("duration")

    def visit_StretchType(self, node: ast.StretchType, context: PrinterState) -> None:
        self.stream.write("stretch")

    @_maybe_annotated
    def visit_CalibrationGrammarDeclaration(
        self, node: ast.CalibrationGrammarDeclaration, context: PrinterState
    ) -> None:
        self._write_statement(f'defcalgrammar "{node.name}"', context)

    @_maybe_annotated
    def visit_CalibrationDefinition(
        self, node: ast.CalibrationDefinition, context: PrinterState
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

    @_maybe_annotated
    def visit_CalibrationStatement(
        self, node: ast.CalibrationStatement, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("cal {")
        # At this point we _should_ be deferring to something else to handle formatting the
        # calibration grammar statements, but we're neither we nor the AST are set up to do that.
        self.stream.write(node.body)
        self.stream.write("}")
        self._end_line(context)

    @_maybe_annotated
    def visit_SubroutineDefinition(
        self, node: ast.SubroutineDefinition, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.stream.write("def ")
        self.visit(node.name, context)
        self._visit_sequence(node.arguments, context, start="(", end=")", separator=", ")
        if node.return_type is not None:
            self.stream.write(" -> ")
            self.visit(node.return_type, context)
        self._visit_statement_list(node.body, context, prefix=" ")
        self._end_line(context)

    def visit_QuantumArgument(self, node: ast.QuantumArgument, context: PrinterState) -> None:
        self.stream.write("qubit")
        if node.size is not None:
            self.stream.write("[")
            self.visit(node.size, context)
            self.stream.write("]")
        self.stream.write(" ")
        self.visit(node.name, context)

    @_maybe_annotated
    def visit_ReturnStatement(self, node: ast.ReturnStatement, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("return")
        if node.expression is not None:
            self.stream.write(" ")
            self.visit(node.expression)
        self._end_statement(context)

    @_maybe_annotated
    def visit_BreakStatement(self, node: ast.BreakStatement, context: PrinterState) -> None:
        self._write_statement("break", context)

    @_maybe_annotated
    def visit_ContinueStatement(self, node: ast.ContinueStatement, context: PrinterState) -> None:
        self._write_statement("continue", context)

    @_maybe_annotated
    def visit_EndStatement(self, node: ast.EndStatement, context: PrinterState) -> None:
        self._write_statement("end", context)

    @_maybe_annotated
    def visit_BranchingStatement(self, node: ast.BranchingStatement, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("if (")
        self.visit(node.condition, context)
        self.stream.write(")")
        self._visit_statement_list(node.if_block, context, prefix=" ")
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
                and not node.annotations
            ):
                context.skip_next_indent = True
                self.visit(node.else_block[0], context)
                # Don't end the line, because the outer-most `if` block will.
            else:
                self._visit_statement_list(node.else_block, context)
                self._end_line(context)
        else:
            self._end_line(context)

    @_maybe_annotated
    def visit_WhileLoop(self, node: ast.WhileLoop, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("while (")
        self.visit(node.while_condition, context)
        self.stream.write(")")
        self._visit_statement_list(node.block, context, prefix=" ")
        self._end_line(context)

    @_maybe_annotated
    def visit_ForInLoop(self, node: ast.ForInLoop, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("for ")
        self.visit(node.type)
        self.stream.write(" ")
        self.visit(node.identifier, context)
        self.stream.write(" in ")
        if isinstance(node.set_declaration, ast.RangeDefinition):
            self.stream.write("[")
            self.visit(node.set_declaration, context)
            self.stream.write("]")
        else:
            self.visit(node.set_declaration, context)
        self._visit_statement_list(node.block, context, prefix=" ")
        self._end_line(context)

    @_maybe_annotated
    def visit_SwitchStatement(self, node: ast.SwitchStatement, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("switch (")
        self.visit(node.target, context)
        self.stream.write(") {")
        self._end_line(context)
        with context.increase_scope():
            for values, block in node.cases:
                self._start_line(context)
                self.stream.write("case ")
                self._visit_sequence(values, context, separator=", ")
                self.stream.write(" {")
                self._end_line(context)
                with context.increase_scope():
                    for statement in block.statements:
                        self.visit(statement, context)
                self._start_line(context)
                self.stream.write("}")
                self._end_line(context)
            if node.default is not None:
                self._start_line(context)
                self.stream.write("default {")
                self._end_line(context)
                with context.increase_scope():
                    for statement in node.default.statements:
                        self.visit(statement, context)
                self._start_line(context)
                self.stream.write("}")
                self._end_line(context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    @_maybe_annotated
    def visit_DelayInstruction(self, node: ast.DelayInstruction, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("delay[")
        self.visit(node.duration, context)
        self.stream.write("]")
        if node.qubits:
            self.stream.write(" ")
            self._visit_sequence(node.qubits, context, separator=", ")
        self._end_statement(context)

    @_maybe_annotated
    def visit_Box(self, node: ast.Box, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("box")
        if node.duration is not None:
            self.stream.write("[")
            self.visit(node.duration, context)
            self.stream.write("]")
        self._visit_statement_list(node.body, context, prefix=" ")
        self._end_line(context)

    def visit_DurationOf(self, node: ast.DurationOf, context: PrinterState) -> None:
        self.stream.write("durationof(")
        if isinstance(node.target, ast.QASMNode):
            self.visit(node.target, context)
        else:
            self._visit_statement_list(node.target, context, prefix="")
        self.stream.write(")")

    def visit_SizeOf(self, node: ast.SizeOf, context: PrinterState) -> None:
        self.stream.write("sizeof(")
        self.visit(node.target, context)
        if node.index is not None:
            self.stream.write(", ")
            self.visit(node.index)
        self.stream.write(")")

    @_maybe_annotated
    def visit_AliasStatement(self, node: ast.AliasStatement, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("let ")
        self.visit(node.target, context)
        self.stream.write(" = ")
        self.visit(node.value, context)
        self._end_statement(context)

    @_maybe_annotated
    def visit_ClassicalAssignment(
        self, node: ast.ClassicalAssignment, context: PrinterState
    ) -> None:
        self._start_line(context)
        self.visit(node.lvalue, context)
        self.stream.write(f" {node.op.name} ")
        self.visit(node.rvalue, context)
        self._end_statement(context)

    def visit_Annotation(self, node: ast.Annotation, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("@")
        self.stream.write(node.keyword)
        if node.command is not None:
            self.stream.write(" ")
            self.stream.write(node.command)
        self._end_line(context)

    def visit_Pragma(self, node: ast.Pragma, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("pragma ")
        self.stream.write(node.command)
        self._end_line(context)
