.. role:: raw-latex(raw)
   :format: latex

.. _pulse-gates:

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
and measurement with a user-selectable pulse grammar.

The entry point to such gate and measurement definitions is the ``defcal`` keyword
analogous to the ``gate`` keyword, but where the ``defcal`` body specifies a pulse-level
instruction sequence on *physical* qubits, e.g.

.. code-block::

   defcal rz(angle[20] theta) $0 { ... }
   defcal measure $0 -> bit { ... }
   defcal measure_iq q -> complex[float[32]] { ... }

Note that this syntax mirrors the 'general' form of ``gate`` definitions in that type
specifiers are **required** for parameters.

We distinguish gate and measurement definitions by the presence of a
return value type in the latter case, analogous to the subroutine syntax
defined earlier. Furthermore, the return value type does not need to return a
classified value but can return some lower level data.

The reference to *physical* rather than *virtual*
qubits is critical because quantum registers are no longer
interchangeable at the pulse level. Due to varying physical qubit
properties a microcode definition of a gate on one qubit will not
perform the equivalent operation on another qubit. To meaningfully
describe gates as pulses we must bind operations to specific qubits.
QASM achieves this by prefixing qubit references with ``$`` to indicate
a specific qubit on the device, e.g. ``$2`` would refer to physical
qubit 2.

One can define a `defcal` using a regular identifier for a qubit, which
causes that calibration definition to be valid for all physical qubits.
This is most likely to be useful for gates that are implemented virtually.
For instance, to define an equivalent `rz` calibration on qubits 0 and 1, we could write

.. code-block::

   defcal rz(angle[20] theta) q { ... }
   // we've defined ``rz`` on arbitrary physical qubits, so we can do:
   rz(3.14) $0;
   rz(3.14) $1;


As a consequence of the need for specialization of operations on
particular qubits, the same symbol may be defined multiple
times, e.g.

.. code-block::

   defcal h $0 { ... }
   defcal h $1 { ... }

and so forth. Some operations require further specialization on
parameter values, so we also allow multiple declarations on the same
physical qubits with different parameter values, e.g.

.. code-block::

   defcal rx(pi) $0 { ... }
   defcal rx(pi / 2) $0 { ... }

Given multiple definitions of the same symbol, the compiler will match
the most specific definition found for a given operation. Thus, given,

#. ``defcal rx(angle[20] theta) q  ...``

#. ``defcal rx(angle[20] theta) $0  ...``

#. ``defcal rx(pi / 2) $0  ...``

the operation ``rx(pi/2) $0`` would match to (3), ``rx(pi) $0`` would
match (2), ``rx(pi/2) $1`` would match (1).

Users specify the grammar used inside ``defcal`` blocks with a
``defcalgrammar "name"`` declaration. One such grammar is a
`textual representation of OpenPulse <openpulse.html>`_ specified by:

.. code-block::

   defcalgrammar "openpulse";

The 'general' gate syntax allows for non-``angle`` parameters. While such parameters may
not be used in the body of ``gate`` defintions, they **may** be used in corresponding
``defcal`` statements. For example,

.. code-block::

   gate var_amp_x(float amplitude) q { x q; }
   defcal var_amp_x(float amplitude) $0 {
      // implement an x gate using the specified control amplitude ...
   }

Note that ``defcal`` and ``gate`` communicate orthogonal information to the compiler. ``gate``\s
define unitary transformation rules to the compiler. The compiler may
freely invoke such rules on operations while preserving the structure of
a circuit as a collection of ``gate``\s and ``subroutine``\s. The ``defcal`` declarations instead define
elements of a symbol lookup table. As soon as the compiler replaces a ``gate``
with a ``defcal`` definition, we have changed the fundamental structure of the
circuit. Most of the time symbols in the ``defcal`` table will also have
corresponding ``gate`` definitions. However, if a user provides a ``defcal`` for a symbol
without a corresponding ``gate``, then we treat such operations like the ``opaque`` gates
of prior versions of OpenQASM.

Inline calibration blocks
~~~~~~~~~~~~~~~~~~~~~~~~~

As calibration grammars may require the ability to insert top-level configuration information, perform program setup, or make inline calls
to calibration-level instructions, OpenQASM supports the ability to declare a ``cal`` block. Within the ``cal`` block the
semantics of the selected ``defcalgrammar`` are valid. The ``cal`` block is of the same scope level as the enclosing block. The
calibration grammar may choose to allow capturing values (with chosen syntax) from within the ``cal``
block that were declared within the containing parent scope.
Values declared within the ``cal`` block are only referenceable from other ``cal`` blocks or ``defcal`` declarations
that may observe that scope as defined by the calibration grammar. Values may not leak back to the block's enclosing scope.
In practice, calibration grammars such as OpenPulse may apply
a global scope to all identifiers in order to declare values shared across all ``defcal`` calls thereby linking them together.

.. code-block::

   OPENQASM 3;
   defcalgrammar "openpulse";

   const float original_freq = 5.9e9;

   cal {
      // Defined within `cal`, so it may not leak back out to the enclosing blocks scope
      float new_freq = 5.2e9;
      // declare global port
      extern port d0;
      // reference `freq` variable from enclosing blocks scope
      frame d0f = newframe(d0, freq, 0.0);

   }

   defcal x $0 {
      waveform xp = gaussian(1.0, 160t, 40dt);
      // References frame and `new_freq` declared in top-level cal block
      play(d0f, xp);
      set_frequency(d0f, new_freq);
      play(d0f, xp);
   }


Restrictions on defcal bodies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The contents of ``defcal`` bodies are subject to the restriction they must have a definite duration
known at compile time, regardless of the parameters passed in or the state of the system when
called. This allows the compiler to properly resolve ``durationof(...)`` calls and
allows for optimizations. If there is to be control flow in the ``defcal``, each branch of the
control flow must have definite and equivalent duration resolvable at compile time. Similarly, loops
must be have a resolvable definite duration at compile time.

For example,  consider the case of a ``reset`` gate. The ``defcal`` for a
``reset`` gate can be composed of a single if statement, provided each branch
of the if statement has definite and equivalent duration.

.. code-block::

   defcal reset $0 {
      bit res = // measure qubit $0
      if (res == 1) {
         // flip the qubit
      } else {
         // delay for an equivalent amount of time
      }
   }

Calibrations in practice
~~~~~~~~~~~~~~~~~~~~~~~~

By their very nature calibrations are transient and unique to a target system.
They are typically generated by automatic calibration routines that are periodically
run on the target system, that are in turn bootstrapped from previous calibrations.
The majority of OpenQASM users will use the default calibrations, however,
for those that want more control, but do not want to bootstrap calibrations for an entire
system. It is expected that the target system provider will provide an include
file to the user. This will contain the declaration of the ``defcalgrammar``, constants,
``defcal``\s and other grammar and system specific components such as ``port``\s,
``waveform``\s and ``frame``\s in the `OpenPulse defcalgrammar <openpulse.html>`. The user
may then plugin to the existing calibrations by defining new calibrations, or overwriting
existing ones by using the same ``port``\s and ``frame``\s.
The example below demonstrates this in practice for a two-qubit,
cross-resonance device using a ``backend.inc`` include file.
The name ``backend.inc`` is arbitrary - it's just a file to be included using the
existing ``include`` mechanism.

.. code-block::

   // backend.inc for openpulse two-qubit device

   defcalgrammar "openpulse";

   const float q0_freq = 5.0e9;
   const float q1_freq = 5.1e9;

   cal {

      extern drag(complex[size] amp, duration l, duration sigma, float[size] beta) -> waveform;
      extern gaussian_square(complex[size] amp, duration l, duration square_width, duration sigma) -> waveform;

      extern port q0;
      extern port q1;

      frame q0_frame = newframe(q0, q0_freq, 0);
      frame q1_frame = newframe(q1, q1_freq, 0);
   }

   defcal rz(angle theta) $0 {
      shift_phase(q0_frame, theta);
   }

   defcal rz(angle theta) $1 {
      shift_phase(q1_frame, theta);
   }

   defcal sx $0 {
      waveform sx_wf = drag(0.2+0.1im, 160dt, 40dt, 0.05);
      play(q0_frame, sx_wf);
   }

   defcal sx $1 {
      waveform sx_wf = drag(0.1+0.05im, 160dt, 40dt, 0.1);
      play(q1_frame, sx_wf);
   }

   defcal cx $1, $0 {
      waveform CR90p = gaussian_square(0.2+0.05im, 560dt, 240dt, 40dt);
      waveform CR90m = gaussian_square(-0.2-0.05im, 560dt, 240dt, 40dt);

      rz(pi/2) $0; rz(-pi/2) $1;
      sx $0; sx $1;
      barrier $0, $1;
      play(q0_frame, CR90p);
      barrier $0, $1;
      sx $0;
      sx $0;
      barrier $0, $1;
      rz(-pi/2) $0; rz(pi/2) $1;
      sx $0; sx $1;
      play(q0_frame, CR90m);
   }

The user would then include the ``backend.inc`` in their own program and use them as demonstrated below

.. code-block::

   OPENQASM 3.0;

   include "backend.inc"

   // Defcal using frames from backend.inc enabling the calibration
   // to "plugin" to the existing calibrations.
   defcal Y90p $0 {
      waveform y90p = drag(0.1-0.2im, 160dt, 40dt, 0.05);
      play(q0_frame, y90p);
   }

   // Teach the compiler what the unitary of a Y90p is
   gate Y90p q {
      rz(-pi/2) q;
      sx q;
   }

   // Use this defcal explicitly
   Y90p $0;
   cx $1, $0;
