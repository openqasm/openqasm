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

length and stretch types
------------------------

The ``length`` type is used denote duration of time. Lengths are positive numbers
that are manipulated at compile time. Lengths have units which can be
any of the following:

-  SI units of time, such as ``ns, µs, ms, s``

-  Backend-dependent unit, ``dt``, equivalent to the duration of one waveform
   sample on the backend

It is often useful to reference the duration of other parts of the
circuit. For example, we may want to delay a gate for twice the duration
of a particular sub-circuit, without knowing the exact value to which
that duration will resolve. Alternatively, we may want to calibrate a
gate using some pulses, and use its duration as a new ``length`` in order to delay
other parts of the circuit. The ``lengthof()`` intrinsic function can be used for this
type of referential timing.

Below are some examples of values of type ``length``.

.. code-block:: c

       // fixed length, in standard units
       length a = 300ns;
       // fixed length, backend dependent
       length b = 800dt;
       // fixed length, referencing the duration of a calibrated gate
       length c = lengthof(defcal);
       // dynamic length, referencing a box within its context
       length d = lengthof(box);

We further introduce a ``stretch`` type which is a sub-type of ``length``. Stretchable lengths
have variable non-negative length that is permitted to grow as necessary
to satisfy constraints. Stretch variables are resolved at compile time
into target-appropriate durations that satisfy a user’s specified design
intent.

Instructions whose duration is specified in this way become “stretchy",
meaning they can extend beyond their “natural length" to fill a span of
time. Stretchy ``delay``'s are the most obvious use case, but this can be extended
to other instructions too, e.g. rotating a spectator qubit while another
gate is in progress. Similarly, a ``gate`` whose definition contains stretchy
delays will be perceived as a stretchy gate by other parts of the
program.

For example, in order to ensure a sequence of gates between two barriers
will be left-aligned (Figure `[fig:alignment] <#fig:alignment>`__\ a),
whatever their actual durations may be, we can do the following:

.. code-block:: c

       barrier q;
       cx q[0], q[1];
       u q[2];
       cx q[3], q[4];
       delay[stretchinf] q[0], q[1];
       delay[stretchinf] q[2];
       delay[stretchinf] q[3], q[4];
       barrier q;

We can further control the exact alignment by giving relative weights to
the stretchy delays (Figure `[fig:alignment] <#fig:alignment>`__\ b):

.. code-block:: c

       stretch g;
       barrier q;
       cx q[0], q[1];
       delay[g];
       u q[2];
       delay[2*g];
       barrier q;

[fig:leftalign]

[fig:leftalignresolved]

Lastly, we distinguish different “orders" of stretch via ``stretchN`` types, where N
is an integer between 0 to 255. ``stretch0`` is an alias for the regular ``stretch``. Higher
order stretches will suppress lower order stretches whenever they appear
in the same scope on the same qubits. A ``stretchinf`` keyword is defined as an
infinitely stretchable length. It will always take precedence, and will
not changed if arithmetic operations are done on it. This is most useful
as a “don’t care" mechanism to specify delays that will just fill
whatever gap is present.

.. code-block:: c

       // stretchable length, with min=0 and max=inf
       stretch e;
       delay[e];
       // higher-order stretch which always mutes lower-order stretch
       stretch2 f;
       delay[2*f];
       // infinitely stretchable length, always anonymous.
       // other instruction don't care about the value to which this resolves.
       delay[stretchinf];

The concepts of ``box`` and ``stretch`` are inspired by the concept of “boxes and glues" in
the TeX language :cite:`knuth1984texbook`. This similarity
is natural; TeXaims to resolve the spacing between characters in order
to typeset a page, and the size of characters depend on the backend
font. In OpenQASM we intend to resolve the timing of different
instructions in order to meet high-level design intents, while the true
length of operations depend on the backend and compilation context.
There are however some key differences. Quantum operations can be
non-local, meaning the lengths set on one qubit can have side effects on
other qubits. The definition of ``length``-type variables and ability to define
multi-qubit stretches is intended to alleviate potential problems from
these side effects. Also contrary to TeX, we prohibit overlapping gates.

Operations on lengths
---------------------

We can add two lengths, or multiply them by a constant, to get new
lengths. These are compile time operations since ultimately all lengths,
including stretches, will be resolved to constants.

.. code-block:: c

       length a = 300ns
       length b = lengthof({x %0})
       stretch c;
       // stretchy length with min=300ns
       length d = a + 2 * c
       // stretchy length with backtracking by up to half b
       length e = -0.5 * b + c

Delays (and other lengthened instructions)
----------------------------------------

OpenQASM and OpenPulse have a ``delay`` instruction, whose duration is defined by
a ``length``. If the length passed to the delay contains stretch, it will become a
stretchy delay. We use square bracket notation to pass these length
parameters, to distinguish them from regular parameters (the compiler
will resolve these square-bracket parameters when resolving timing ).

Even though a ``delay`` instruction implements the identity channel in the ideal
case, it is intended to provide explicit timing. Therefore an explicit ``delay``
instruction will prevent commutation of gates that would otherwise
commute. For example in
Figure `[fig:delaycommute] <#fig:delaycommute>`__\ a, there will be an
implicit delay between the ``cx`` gates on qubit 0. However, the ``rz`` gate is
still free to commute on that qubit, because the delay is implicit. Once
the delay becomes explicit (perhaps at lower stages of compilation),
gate commutation is prohibited
(Figure `[fig:delaycommute] <#fig:delaycommute>`__\ b).

Instructions other than delay can also have variable duration, if they
are explicitly defined as such. They can be called by passing a valid ``length`` as
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
time across all qubits, and ends simultaneously across all qubits. For
this reason, a ``barrier`` instruction is exactly equivalent to a ``delay`` of a length zero
on the qubits involved.

.. code-block:: c

       cx q[0], q[1];
       cx q[2], q[3];
       // delay for 200 samples starting from the end of the longest cx
       delay[200dt] q[0:3];

A ``length`` can be composed of positive or negative natural length, and of
positive stretch. After resolving the stretch, the instruction must end
up with non-negative duration.

For example, the code below inserts a dynamical decoupling sequence
where the \*centers\* of pulses are equidistant from each other. We
specify correct lengths for the delays by using backtracking operations
to properly take into account the finite length of each gate.

.. code-block:: c

   stretch s, t;
   length start_stretch = s - .5 * lengthof({x %0;})
   length middle_stretch = s - .5 * lengthof({x %0;}) - .5 * lengthof({y %0;}
   length end_stretch = s - .5 * lengthof({y %0;})

   delay[start_stretch] %0;
   x %0;
   delay[middle_stretch] %0;
   y %0;
   delay[middle_stretch] %0;=
   x %0;
   delay[middle_stretch] %0;
   y %0;
   delay[end_stretch] %0;

   cx %2, %3;
   delay[t] %1;
   cx %1, %2;
   u %3;

Boxed expressions
-----------------

We introduce a ``box`` expression for scoping a particular part of the circuit.
A boxed subcircuit can never be inlined (until target code generation
time), and optimizations across the boundary of a box are forbidden. The
contents inside the box can be optimized. The contents around the box
can be optimized too, e.g. it is permissible to commute a gate past a
box by knowing the unitary implemented by the box. Delays that are
within a box are implementation details of the box; they are invisible
to the outside scope and therefore do not prevent commutation.

We introduce a ``boxas`` expression for labeling a box. We primarily use this to
later refer to the length of this box. Boxed expressions are good for
this because their contents are isolated and cannot be combined with
gates outside the box. Therefore, no matter how the contents of the box
get optimized, the ``lengthof(boxlabel`` has a well-defined meaning.

.. code-block:: c

       boxas mybox {
           cx q[0], q[1];
           delay[200ns] q[0];
       }
       delay[length(mybox)] q[2], q[3];
       cx q[2], q[3];

We introduce a ``boxto`` expression. The contents of it will be boxed, and in
addition a total duration will be assigned to the box. This is useful
for conditionals where the box will declare a hard deadline. The natural
length of the box must be smaller than the declared boxto duration,
otherwise a compile-time error will be raised. The stretch inside the
box will always be set to fill the difference between the declared
length and the natural length.

.. code-block:: c

      // defines a 1ms box whose content is just a centered CNOT
       boxto 1ms {
           stretch a;
           delay[a] q;
           cx q[0], q[1];
           delay[a] q;
       }

Barrier instruction
-------------------

The ``barrier`` instruction of OpenQASM 2 prevents commutation and gate reordering
on a set of qubits across its source line. The syntax is ``barrier qregs|qubits;`` and can be seen
in the following example

.. code-block:: c

   cx r[0], r[1];
   h q[0];
   h s[0];
   barrier r, q[0];
   h s[0];
   cx r[1], r[0];
   cx r[0], r[1];

This will prevent an attempt to combine the CNOT gates but will not
constrain the pair of ``h s[0];`` gates, which might be executed before or after the
barrier, or cancelled by a compiler.
