.. role:: raw-latex(raw)
   :format: latex
..

Circuit timing
==============

A key aspect of expressing code for quantum experiments is the ability
to control the timing of gates and pulses. Examples include
characterization of decoherence and crosstalk, dynamical decoupling,
dynamically corrected gates, and gate scheduling. This can be a
challenging task given the potential heterogeneity of calibrated gates
and their various durations. It is useful to specify gate timing and
parallelism in a way that is independent of the precise duration and
implementation of gates at the pulse-level description. In other words,
we want to provide the ability to capture *design intent* such as “space
these gates evenly to implement a higher-order echo decoupling sequence"
or “implement this gate as late as possible".

.. _duration-and-stretch:

Duration and stretch types
---------------------------

The ``duration`` type is used denote increments of time. Durations are positive real numbers
that are manipulated at compile time. Durations must be followed by time units which can be
any of the following:

-  SI units of time: ``ns, µs or us, ms, s``

-  Backend-dependent unit, ``dt``, equivalent to the duration of one waveform
   sample on the backend

Units can appear attached to the numerical value, or immediately following
separated only by blanks or tabs. ``1000ms`` is the same as ``1000 ms``.

It is often useful to reference the duration of other parts of the
circuit. For example, we may want to delay a gate for twice the duration
of a particular sub-circuit, without knowing the exact value to which
that duration will resolve. Alternatively, we may want to calibrate a
gate using some pulses, and use its duration as a new ``duration`` in order to delay
other parts of the circuit. The ``durationof()`` intrinsic function can be used for this
type of referential timing.

Below are some examples of values of type ``duration``.

.. code-block:: c

       // fixed duration, in standard units
       duration a = 300ns;
       // fixed duration, backend dependent
       duration b = 800dt;
       // fixed duration, referencing the duration of a calibrated gate
       duration c = durationof({x $3;});

We further introduce a ``stretch`` type which is a sub-type of ``duration``. Stretchable durations
have variable non-negative duration that are permitted to grow as necessary
to satisfy constraints. Stretch variables are resolved at compile time
into target-appropriate durations that satisfy a user’s specified design
intent.

Instructions whose duration are specified in this way become “stretchy",
meaning they can extend beyond their “natural duration" to fill a span of
time. Stretchy ``delay``'s are the most obvious use case, but this can be extended
to other instructions too, e.g. rotating a spectator qubit while another
gate is in progress. Similarly, a ``gate`` whose definition contains stretchy
delays will be perceived as a stretchy gate by other parts of the
program.

.. _fig_alignment:
.. multifigure::
   :labels: a b

   .. image:: ../qpics/d1.svg

   .. image:: ../qpics/d2.svg

   Arbitrary alignment of gates in time using stretchy delays. a) left-justified
   alignment b) alignment of a short gate at the 1/3 point of a longer gate.

For example, in order to ensure a sequence of gates between two barriers
will be left-aligned (:numref:`fig_alignment`\a),
whatever their actual durations may be, we can do the following:

.. code-block:: c

       qubit[5] q;
       barrier q;
       cx q[0], q[1];
       U(pi/4, 0, pi/2) q[2];
       cx q[3], q[4];
       stretch a;
       stretch b;
       stretch c;
       delay[a] q[0], q[1];
       delay[b] q[2];
       delay[c] q[3], q[4];
       barrier q;

We can further control the exact alignment by giving relative weights to
the stretchy delays (:numref:`fig_alignment`\b):

.. code-block:: c

       qubit[5] q;
       stretch g;
       barrier q;
       cx q[0], q[1];
       delay[g];
       u q[2];
       delay[2*g];
       barrier q;

The concepts of ``box`` (see :ref:`Boxed expressions`) and ``stretch`` are inspired by the
concept of “boxes and glues" in the TeX language :cite:`knuth1984texbook`. This similarity
is natural; TeX aims to resolve the spacing between characters in order
to typeset a page, and the size of characters depend on the backend
font. In OpenQASM we intend to resolve the timing of different
instructions in order to meet high-level design intents, while the true
duration of operations depend on the backend and compilation context.
There are however some key differences. Quantum operations can be
non-local, meaning the durations set on one qubit can have side effects on
other qubits. The definition of ``duration``-type variables and ability to define
multi-qubit stretches is intended to alleviate potential problems from
these side effects. Also contrary to TeX, we prohibit overlapping gates.

Operations on durations
-----------------------

We can add/subtract two durations, or multiply or divide them by a constant, to get a new
duration. Division of two durations results in a machine-precision float 
(see :ref:`divideDuration`). Negative durations are allowed, however
passing a negative duration to a ``gate[duration]`` or ``box[duration]`` expression will result in an error.
All operations on durations happen at compile time since ultimately all
durations, including stretches, will be resolved to constants.

.. code-block:: c

       duration a = 300ns;
       duration b = durationof({x $0;});
       stretch c;
       // stretchy duration with min=300ns
       stretch d = a + 2 * c;
       // stretchy duration with backtracking by up to half b
       stretch e = -0.5 * b + c;

Delays (and other duration-based instructions)
----------------------------------------------

OpenQASM and OpenPulse have a ``delay`` instruction, whose duration is defined by
a ``duration``. If the duration passed to the delay contains stretch, it will become a
stretchy delay. We use square bracket notation to pass these duration
parameters, to distinguish them from regular parameters (the compiler
will resolve these square-bracket parameters when resolving timing).

Even though a ``delay`` instruction implements the identity operator in the ideal
case, it is intended to provide explicit timing. Therefore an explicit ``delay``
instruction will prevent commutation of gates that would otherwise
commute. For example in
:numref:`fig_delaycommute`\a , there will be an
implicit delay between the ``cx`` gates on qubit 0. However, the ``rz`` gate is
still free to commute on that qubit, because the delay is implicit. Once
the delay becomes explicit (perhaps at lower stages of compilation),
gate commutation is prohibited (Figure :numref:`fig_delaycommute`\b).

.. _fig_delaycommute:
.. multifigure::
   :labels: a b

   .. image:: ../qpics/d3.svg

   .. image:: ../qpics/d4.svg

   Implicit vs. explicit delay. a) An implicit delay exists on :math:`q[0]`, but it
   is not part of the circuit description. Thus this circuit does not care about
   timing and the :math:`RZ` gate is free to commute on the top wire. b) An explicit
   delay is part of the circuit description. The timing is consistent and can
   be resolved if and only if this delay is exactly the same duration as :math:`RY` on
   :math:`[1]`. The delay is like a barrier in that it prevents commutation on that
   wire. However :math:`RZ` can still commute before the :math:`CNOT` if it has
   duration :math:`0`.


.. _fig_dcg:
.. multifigure::
   :labels: a b

   .. image:: ../qpics/d5.svg

   .. image:: ../qpics/d6.svg

   Dynamically corrected CNOT gate where the spectator has a rotary pulse. The
   rotary gates are stretchy, and the design intent is to interleave a "winding"
   and "unwinding" that is equal to the total duration of the CNOT. We do this
   without knowledge of the CNOT duration, and the compiler resolves them to the
   correct duration during lowering to the target backend.

.. _fig_dd:
.. multifigure::

   .. image:: ../qpics/d7.svg

   Dynamical decoupling of a spectator qubit using finite-duration DD pulses.
   The boxes are intentionally drawn to scale to give a sense of how finite gate
   durations affect circuit timing. This design intent can be expressed by
   defining a single stretch variable "equal" that corresponds to the distance
   between equidistant gate centers. The other durations which correspond to
   actual circuit delays are derived by simple arithmetic. Given a
   target system with calibrated X and Y gates, the solution to the stretch
   problem can be found.

Instructions other than delay can also have variable duration, if they
are explicitly defined as such. They can be called by passing a valid ``duration`` as
their duration. Consider for example a rotation called ``rotary`` that is applied
for the entire duration of some other gate.

.. code-block:: c

       const amp = /* number */;
       stretch a;
       rotary(amp)[250ns] q;   // square brackets indicates duration
       rotary(amp)[a] q;       // a rotation that will stretch as needed

A multi-qubit ``delay`` instruction is *not* equivalent to multiple single-qubit
``delay`` instructions. Instead a multi-qubit delay acts as a synchronization
point on the qubits, where the delay begins from the latest non-idle
time across all qubits, and ends simultaneously across all qubits.

.. code-block:: c

       cx q[0], q[1];
       cx q[2], q[3];
       // delay for 200 samples starting from the end of the longest cx
       delay[200dt] q[0:3];

A ``duration`` can be composed of positive or negative durations, and of
positive stretches. After resolving the stretches, the instruction must end
up with non-negative duration.

For example, the code below inserts a dynamical decoupling sequence
where the \*centers\* of pulses are equidistant from each other. We
specify correct durations for the delays by using backtracking operations
to properly take into account the finite duration of each gate.

.. code-block:: c

   stretch a;
   stretch b;
   duration start_stretch = a - .5 * durationof({x $0;});
   duration middle_stretch = a - .5 * duration0({x $0;}) - .5 * durationof({y $0;});
   duration end_stretch = a - .5 * durationof({y $0;});

   delay[start_stretch] $0;
   x $0;
   delay[middle_stretch] $0;
   y $0;
   delay[middle_stretch] $0;
   x $0;
   delay[middle_stretch] $0;
   y $0;
   delay[end_stretch] $0;

   cx $2, $3;
   delay[b] $1;
   cx $1, $2;
   u $3;

.. _Boxed expressions

Boxed expressions
-----------------

We introduce a ``box`` statement for scoping the timing of a particular part of the circuit.
A boxed subcircuit is different from a ``gate`` or ``def`` subroutine, in that it is merely 
an enclosure to a piece of code within the larger scope which constains it. This can be used to
signal permissible logical-level optimizations to the compiler: optimizing operations within
a ``box`` definition is permitted, and optimizations that move operations from one side to
the other side of a box are permitted, but moving operations either into or out of the box as
part of an optimization is forbidden. The compiler can also infer a description of the
operation which a ``box`` definition is meant to realise, allowing it to re-order gates around
the box. For example, consider a dynamical decoupling sequence inserted in a part of the circuit:

.. code-block:: c

    rx(2*π/12) q;
    box {
        delay[ddt] q;
        x q;
        delay[ddt] q;
        x q;
        delay[ddt] q;
    }
    rx(3*π/12) q;

By boxing the sequence, we create a box that implements the identity. The compiler is now free
to commute a gate past the box by knowing the unitary implemented by the box:

.. code-block:: c

    rx(5*π/12) q;
    box {
        delay[ddt] q;
        x q;
        delay[ddt] q;
        x q;
        delay[ddt] q;
    }

The compiler can thus perform optimizations without interfering with the implmentation of the
dynamical decoupling sequence. 

As with other operations, we may use square brakets to assign a duration to a box: this can be
used to put hard constraints on the execution of a particular sub-circuit by requiring it to
have the assigned duration. This can be useful in scenarios where the exact duration of a piece
of code is unknown (*e.g.*, if it is runtime dependent), but where it would be helpful to impose
a duration on it for the purpose of scheduling the larger circuit. For example, if the duration
of the parameterized gates ``mygate1(a, b), mygate2(a, b)`` depend on values of the variables
``a`` and ``b`` in a complex way, but an offline calculation has shown that the total will never
require more than 150ns for all valid combinations:

.. code-block:: c

    // some complicated circuit that gives runtime values to a, b
    box [150ns] {
        delay[str1] q1; // Schedule as late as possible within the box
        mygate1(a, a+b) q[0], q[1];
        mygate2(a, a-b) q[1], q[2];
        mygate1(a-b, b) q[0], q[1];
    }


Barrier instruction
-------------------

The ``barrier`` instruction of OpenQASM 2 prevents commutation and gate reordering
on a set of qubits across its source line. The syntax is ``barrier qregs|qubits;`` and can be seen
in the following example

.. code-block:: c

   cx r[0], r[1];
   h q[0];
   h a[0];
   barrier r, q[0];
   h a[0];
   cx r[1], r[0];
   cx r[0], r[1];

This will prevent an attempt to combine the CNOT gates but will not
constrain the pair of ``h a[0];`` gates, which might be executed before or after the
barrier, or cancelled by a compiler.

A ``barrier`` is similar to ``delay[0]``. The main difference is that ``delay`` indicates a fully
scheduled series of instructions, whereas ``barrier`` implies an ordering constraint that will be
resolved by the compiler at a later stage.

A barrier can also be invoked without arguments, in which case the argument is assumed to be all
qubits.
