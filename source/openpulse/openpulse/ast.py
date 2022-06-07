"""

========================================
Abstract Syntax Tree (``openpulse.ast``)
========================================

.. currentmodule:: openpulse.ast

The reference abstract syntax tree (AST) for OpenPulse programs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

# Re-export the existing AST classes from openqasm3
# pylint: disable=unused-import
from openqasm3.ast import *

# The statement above does not import ExternArgument. Remove when it is fixed.
# pylint: disable=unused-import
from openqasm3.ast import ExternArgument

# From Pulse grammar
class WaveformType(ClassicalType):
    """
    Leaf node representing the ``waveform`` type.
    """


class PortType(ClassicalType):
    """
    Leaf node representing the ``port`` type.
    """


class FrameType(ClassicalType):
    """
    Leaf node representing the ``frame`` type.
    """


@dataclass
class CalibrationBlock(Statement):
    """
    Cal block

    Example::

        cal {

            extern drag(complex[size], duration, duration, float[size]) -> waveform;
            extern gaussian_square(complex[size], duration, duration, duration) -> waveform;

            port q0 = getport("q", $0);
            port q1 = getport("q", $1);

            frame q0_frame = newframe(q0_freq, 0);
            frame q1_frame = newframe(q1_freq, 0);
        }
    """

    body: List[Statement]


# Override the class from openqasm3
@dataclass
class CalibrationDefinition(Statement):
    # pylint: disable=E0102
    """
    Calibration definition

    Example::

        defcal rz(angle[20] theta) $q {
            shift_phase(drive($q), -theta);
        }
    """

    name: Identifier
    arguments: List[ClassicalArgument]
    qubits: List[Identifier]
    return_type: Optional[ClassicalType]
    body: List[Statement]
