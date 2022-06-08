import io

from openqasm3.printer import Printer as QASMPrinter
from openqasm3.printer import PrinterState

import openpulse.ast as ast


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


class Printer(QASMPrinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit_FrameType(self, node: ast.FrameType, context: PrinterState) -> None:
        self.stream.write("frame")

    def visit_PortType(self, node: ast.PortType, context: PrinterState) -> None:
        self.stream.write("port")

    def visit_WaveformType(self, node: ast.WaveformType, context: PrinterState) -> None:
        self.stream.write("waveform")

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
        self._end_line(context)
        with context.increase_scope():
            for statement in node.body:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)

    def visit_CalibrationBlock(self, node: ast.CalibrationBlock, context: PrinterState) -> None:
        self._start_line(context)
        self.stream.write("cal {")
        self._end_line(context)
        with context.increase_scope():
            for statement in node.body:
                self.visit(statement, context)
        self._start_line(context)
        self.stream.write("}")
        self._end_line(context)
