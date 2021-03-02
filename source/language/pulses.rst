.. role:: raw-latex(raw)
   :format: latex
..

Pulse-level descriptions of gates and measurement
=================================================

To induce the quantum gates and measurements of a circuit, qubits are
manipulated with classically-controlled stimulus fields. The details of
these stimuli are typically unique per-qubit and may vary over time due
to instabilities in the underlying systems. Furthermore, there is
significant interest in applying optimal control methodologies to the
construction of these controls in order to optimize gate and circuit
performance. As a consequence, we desire to connect gate-level
instructions to the underlying microcoded
:cite:`wilkesBestWayDesign1989` stimulus programs emitted by
the controllers to implement each operation. In OpenQASM we expose
access to this level of control with pulse-level definitions of gates
and measurement with user-selectable pulse grammar. A future document
will define a textualized representation of one such grammar, OpenPulse.
Here we restrict ourselves to defining the necessary interfaces within
OpenQASM to these pulse-level definitions of gates and measurement.

The entry point to such gate and measurement definitions is the ``defcal`` keyword
analogous to the ``gate`` keyword, but where the ``defcal`` body specifies a pulse-level
instruction sequence on *physical* qubits, e.g.

.. code-block:: c

   defcal rz(angle[20]:theta) $0 { ... }
   defcal measure $0 -> bit { ... }

We distinguish gate and measurement definitions by the presence of a
return value type in the latter case, analogous to the subroutine syntax
defined earlier. The reference to *physical* rather than *virtual*
qubits is critical because quantum registers are no longer
interchangeable at the pulse level. Due to varying physical qubit
properties a microcode definition of a gate on one qubit will not
perform the equivalent operation on another qubit. To meaningfully
describe gates as pulses we must bind operations to specific qubits.
QASM achieves this by prefixing qubit references with ``$`` to indicate
a specific qubit on the device, e.g. ``$2`` would refer to physical
qubit 2.

One can define a `defcal` using an arbitrary `$` identifier, provided that gate is called using physical
qubits. For instance, to define an equivalent `rz` calibration on qubits 0 and 1, we could write

.. code-block:: c

   defcal rz(angle[20]:theta) $q { ... }
   // we've defined ``rz`` on arbitrary physical qubits, so we can do:
   rz(3.14) $0;
   rz(3.14) $1;


As a consequence of the need for specialization of operations on
particular qubits, the same symbol may be defined multiple
times, e.g.

.. code-block:: c

   defcal h $0 { ... }
   defcal h $1 { ... }

and so forth. Some operations require further specialization on
parameter values, so we also allow multiple declarations on the same
physical qubits with different parameter values, e.g.

.. code-block:: c

   defcal rx(pi) $0 { ... }
   defcal rx(pi / 2) $0 { ... }

Given multiple definitions of the same symbol, the compiler will match
the most specific definition found for a given operation. Thus, given,

#. ``defcal rx(angle[20]:theta) $q  ...``

#. ``defcal rx(angle[20]:theta) $0  ...``

#. ``defcal rx(pi / 2) $0  ...``

the operation ``rx(pi/2) $0`` would match to (3), ``rx(pi) $0`` would
match (2), ``rx(pi/2) $1`` would match (1).

Users specify the grammar used inside ``defcal`` blocks with a ``defcalgrammar "name"`` declaration.
For instance,

.. code-block:: c

   defcalgrammar "openpulse";

specifies that all `defcal`'s will use the "openpulse" grammar.


Note that ``defcal`` and ``gate`` communicate orthogonal information to the compiler. ``gate``'s
define unitary transformation rules to the compiler. The compiler may
freely invoke such rules on operations while preserving the structure of
a circuit as a collection of ``gate``'s and ``subroutine``'s. The ``defcal`` declarations instead define
elements of a symbol lookup table. As soon as the compiler replaces a ``gate``
with a ``defcal`` definition, we have changed the fundamental structure of the
circuit. Most of the time symbols in the ``defcal`` table will also have
corresponding ``gate`` definitions. However, if a user provides a ``defcal`` for a symbol
without a corresponding ``gate``, then we treat such operations like the ``opaque`` gates
of prior versions of OpenQASM.
