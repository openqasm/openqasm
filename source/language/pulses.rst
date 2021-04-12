.. role:: raw-latex(raw)
   :format: latex
..

Pulse-level descriptions of gates and measurement
=================================================

To induce the quantum gates and measurements of a circuit, qubits are
manipulated with classically-controlled stimulus pulses. These stimuli
are typically unique per-qubit and may vary over time due
to instabilities in the underlying systems. Furthermore, there is
significant interest in applying optimal control methodologies to the
construction of these controls in order to optimize gate and circuit
performance. As a consequence, we desire to connect gate-level
instructions to the underlying microcoded
:cite:`wilkesBestWayDesign1989` stimulus programs emitted by
the controllers to implement each operation. In OpenQASM we expose
access to this level of control with pulse-level definitions of gates
and measurement with a user-selectable pulse grammar.

The entry point to such gate and measurement definitions is the ``defcal`` keyword
analogous to the ``gate`` keyword, but where the ``defcal`` body specifies a pulse-level
instruction sequence on *physical* qubits. The reference to *physical* rather than *virtual*
qubits is critical as quantum registers are not interchangeable at the pulse level. Due to varying
physical qubit properties a microcode definition of a gate on one qubit will not perform the
equivalent operation on another qubit. To meaningfully describe gates as pulses we must bind
operations to specific qubits. QASM achieves this by prefixing qubit references with ``$`` to
indicate a specific qubit on the device, e.g. ``$2`` would refer to physical qubit 2, while ``$q``
is a wildcard reference to any physical qubit.

Some example ``defcal`` blocks are

.. code-block:: c

   defcal rz(angle[20]:theta) $q { ... }
   defcal measure $q -> bit { ... }
   defcal measure_iq $q -> complex[32] { ... }

where inside the `{...}` would be instructions from a selected pulse grammar.

We distinguish gate and measurement definitions by the presence of a
return value type in the latter case, analogous to the subroutine syntax
defined earlier. The return type can be any supported classical type. Discriminated
values will return a bit, but one might also be interested in IQ data (ie a complex type)
or other return types.

As a consequence of the need for specialization of operations on particular qubits, the same symbol
may be defined multiple times, e.g.

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

Users specify the grammar used inside ``defcal`` blocks with a ``defcalgrammar "name" VERSION``
declaration. One such grammar is `OpenPulse <openpulse.html>`_ specified by:

.. code-block:: c

   defcalgrammar "openpulse" 1;

where ``1`` is the version number of the grammar. The ``defcalgrammar`` line
must appear prior to any ``defcal`` definition.


``defcal`` and ``gate`` declarations communicate orthogonal information to the compiler. ``gate``'s
define unitary transformation rules to the compiler. The compiler may
freely invoke such rules on operations while preserving the structure of
a circuit as a collection of ``gate``'s and ``subroutine``'s. The ``defcal`` declarations instead define
elements of a symbol lookup table. As soon as the compiler replaces a ``gate``
with a ``defcal`` definition, we have changed the fundamental structure of the
circuit. Most of the time symbols in the ``defcal`` table will also have
corresponding ``gate`` definitions. However, if a user provides a ``defcal`` for a symbol
without a corresponding ``gate``, then we treat such operations like the ``opaque`` gate
of prior versions of OpenQASM.

Restrictions on defcal bodies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The contents of ``defcal`` bodies are subject to some restrictions. This is
similar to how boxed expressions work.

- They must have a definite length resolvable at compilation time, regardless of the parameters passed in or
  the state of the system when called. This allows the compiler to properly
  resolve ``lengthof(...)`` calls and allowing for optimizations.
- No control flow is allowed within a ``defcal`` block (with one exception,
  see below). This follows from the definite length requirement.

The sole exception to the second rule is a ``reset`` gate. The ``defcal`` for a
``reset`` gate is permitted to have a single if statement, provided each branch
of the if statement has definite and equivalent length.

.. code-block:: c

   defcal reset $0 {
      bit res = measure $0;
      if (res == 1) {
         // flip the qubit
      } else {
         // delay for an equivalent amount of time
      }
   }

Generic defcal's
~~~~~~~~~~~~~~~~~~~~~

For certain experiments, it may not be possible to encode all pulse functionality within a gate
definition. For instance, consider the case of qubit spectroscopy. A frequency input is required
to the drive stimulus pulse. For this reason, we allow ``defcal``'s which may be called directly
within OpenQASM. They must obey the same rules as gate/measurement ``defcal``'s (no control flow,
up to one return type), but can take any classical argument. For instance, one might define for
spectroscopy

.. code-block:: c

   defcal sp_cal(float[64] freq) $q -> complex[64] {...}
