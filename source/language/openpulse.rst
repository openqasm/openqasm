OpenPulse Grammar
=================

In addition to OpenQASM instructions, ``defcal`` blocks may contain OpenPulse
instructions. Certain OpenPulse instructions are further restricted to only
appearing inside of a ``defcal`` block.

These instructions are motivated by the original OpenPulse specification which
was defined as a JSON wire-format for pulse-level quantum programs in the paper
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment <https://arxiv.org/abs/1809.03452>`_.
The text format described here has several advantages over the equivalent JSON
format:

- It is more readable
- Absolute time is handled through built-in timekeeping instructions
- Gates and classical instructions can be mixed in with the pulses to create far richer calibrations
- Pulse definitions are tied to circuit instructions rather than circuit programs
- Richer ability to compose pulses as signals and manage the relationship between pulses.

Interacting with qubits at the level of pulses is onerous and pulse programming is by definition
less portable than the circuit model. The OpenPulse ``defcalgrammar`` defines the
concept of ``channel``s and ``signal``s. The ``signal`` defines a *logical* signal within a natural
DSP block diagram formalism, which are then emitted or produced by transmitting them on a *logical*
``channel`` in the target device. It is the responsibility of the target device's compiler to map
this idealized *logical* signal to *physical* target hardware to emit the corresponding *physical*
signal. This formalism enables the pulse programmer to worry about only specifying the desired signal
and delegates the responsibility to faithfully implement this signal to the compiler, abstracting away
the complexities of the device's signal generation hardware.


Signals
-------

A ``signal`` is a generalization of a concept of a `pulse`.
A signal consists of a discrete time-dependent function :math:`s(t), ℤ->ℂ` of max unit-norm
and a clock-value (marker) :math:`t ∈ ℤ, t >= 0`. In a sense, the time :math:`t` is an "index" into the signal.
The clock-value is propagated from its child signal with the initial value originating from the clock of the channel on which the signal is applied.

Openpulse supplies many types of builtin signal production operations such as an:

- ``envelope`` - A complex envelope - ``envelope signal = [0.0+1.0j, ..., 1.0+0.0j];``
- ``wave`` - A signal representing a carrier wave such as an oscillator - ``wave frame = osc(5e9, 2*pi);``

Signals may be composed via transformation functions to form new signals that are derived from the input parent signals. For example ``new_signal = mix(envelope, wave);``
produces a new child signal that is a mixture of its parent envelope and carrier wave signals. Combining signals in this way forms a "signal network", where signals are
edges between signal production/transformation nodes. Within the signal programming model, signals are constructed via composition. Signals may be emitted or produced by a ``channel``.
The clock-value of a signal is propagated from its clock. Within this formalism, builtin signal-generation operations such as ``gaussian`` are ``source`` nodes that produce a signal (ie., no input edges).

.. code-block: none
    sig1 sig2
      |   |
      v   v
  transformation
        |
        v
       (root) sig3

A signal network has a correspondence with a traditional microwave block diagram.
Unlike qubit operations, signals are not linear and may be reused by splitting them, ie., they may be cloned.
In practice, we allow reusing the named edged without requiring an explicit split operation.

.. code-block: none
       sig1
        |
        v
      split
       / \
      v   v
     re  im
      |   |
      v   v
    sig2 sig3

A signal is defined by its ancestor signal production/transformation nodes,
:math:`s_n(t) = f_{n-1}(s_{n-1}^{(0)}(t), s_{n-1}^{(j)}(t)) = f_{n-1}(f_{n-1}^{(0)}(s_{n-2}^{(0)}, ...), ..., f_{n-2}^{j}(s_{n-2}^{(j)}, ...))`.
This automatically gives many nice properties. For example, if all dependent signals are differentiable, so must be the final signal by the chain rule.

When outputting a signal on a ``channel`` the intermediate signals in the signal network are only useful insofar as to describe the output signal.
This enables the compiler to restructure the signal network to better map to the available hardware.
For example, if the hardware is capable of providing support for a ``carrier``, it may natively represent a signal of the form ``mix(envelope, carrier)``,
otherwise it may choose to rewrite the signal as a sidebanded envelope.

Signal production operations
----------------------------

Signal production operations are signal ``sources`` that maintain clock relationships when coupled to an output channel.

- ``envelope``: Maintain an internal clock that begins at :math:`t=0` for every usage with a channel, eg., :math:`t_{envelope} = t_{ch} - t0_{ch}`.
This is to enable the reuse of an envelope signal many times. Are parameterized such that :math:`s(0) = 0`, :math:`s(t>=tf) = 0`.
  -  ``waveform`` - ``envelope wf1 = [0.1, 1.j, 0.1 - 0.2j, ...];``
  - ``gaussian(amp: complex, duration: length, sigma: length)``,
  - ``gaussian_square(amp: complex, duration: length, sigma: length, square_width: length)``,
  - ``drag(amp: complex, duration: length, sigma: length, beta: float)``,
  - ``constant(amp: complex, duration: length)``

- ``wave(amp: complex, freq: float, phase: angle)`` - Characterized by ``amp``, ``freq`` and ``phase``.
This modification occurs at the current time of the signal's local clock.
The clock is determined by the clock of the controlling physical channel, eg., :math:`t_{wave} = t_{ch}`.
Waves are a named three-tuple and may be modified with dot notation during real-time execution, eg., ``wave.phase += pi;``.
Updates to a wave's properties will therefore propagate forward in time for future uses as determined by the applied physical channel.
In this way, persistent amplitude/phase/frequency-updates may be applied.

- ``osc``: :math:`Ae^{i(wt+\phi)}`, Sine/Cosine waves can be obtained by deriving with ``re``/``im``.
- ``sawtooth``
- ``square``
- ``triangle``

Signal composition operations
-----------------------------

Each takes as input one or more signals, applies a transformation, and produces a new signal. Note these do not mutate the input signals but are more akin to piping the signal into a transfer function. Signals are classical and may be copied without a problem. It is up to the compiler to choose how to implement the required transformations on hardware:

- ``shift(sig: signal, time: length)`` - Shift the signal by ``time`` by incrementing the signal clock to be passed to ancestor signal ``sig``.
- ``set(sig: signal, time: length)`` - Ignore the propagated child signal clock and replace it with ``time`` to be propagated to all ancestor nodes.
- ``mix(sig: signal, sig: signal) -> signal`` - Mix two input signals to produce a new signal. This is equivalent to the product signal :math:`s(t_i) = s_1(t_i) x s_2(t_i)`.
- ``sum(sig: signal, sig: signal) -> signal`` - Sum two input signals to produce a new signal.
- ``piecewise(sig0: signal, sig1: signal, time: length) -> signal`` - Output ``sig``.
- ``offset(sig: signal, amount: complex) -> signal`` - Offset the input signal by an ``amount``.
- ``scale(sig: signal, factor: complex) -> signal``  - Scale the input signal by a ``factor``.
- ``conj(sig: signal) -> signal`` - Conjugate the input signal.
- ``re(sig: signal) -> signal`` - Real component of input signal.
- ``im(sig: signal) -> signal`` - Imaginary component of input signal.
- ``abs(sig: signal) -> signal`` - Transform signal as norm of input. signal
- ``phase(sig: signal, ang: angle) -> signal`` - Signal with relative phase, ``ang``.


Channels
--------

Channels map to a hardware resource, which can play signals(pulses) to manipulate a qubit
or capture a signal from the qubit to perform a measurement.

Within the openpulse grammar channels have two critical responsibilities:

1. They are the interface between a logical ``signal`` (and correspondingly gates)
to configured control hardware in the target device. They are representations of the
exposed IO ports of the device.
2. They are responsible for maintaining a counter for the current *time* on a channel
within a program's execution with respect to the global program time. As instructions
are applied to the channel this counter is incremented. As each channel maintains its
own clock, it is possible to apply instructions sequentially within the ``defcal``
declaration and have the ``signal``s be emitted simultaneously at runtime as determined
by the ``channel``s clocks' at call time.

There is a many-to-many relationship between qubits and channels.
One qubit may be controlled by multiple channels.
Pulses applied on different channels have different physical interactions with that qubit.
Inversely, a channel may also affect many qubits. For instance,
a channel could manipulate the coupling between two neighboring qubits, or
could even reference multiple qubits coupled in a chain.

Channels are defined by each vendor for every target device. It is expected that vendors
of quantum hardware provide the appropriate channel names and qubit mappings
as configuration information to end users.

There are two kinds of channels:

- transmit channels (``txch``): For emitting a ``signal`` to an output port on the quantum device.
- receive channels (``rxch``): For capturing an output signal from a quantum device to produce a logical ``signal``.


Signals are transmitted and received with the *transmit* ``tx`` and *receive* ``rx`` instructions
which may be called on ``txch``s and ``rxch``s respectively.


Channel signal output operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If channel production operations are signal ``sources``, the ``transmit`` operation is the signal ``sink`` (ie., no output edges). Piping the signal out of the logical Openpulse domain into the physical hardware.

- ``transmit(txchannel ch, length duration, signal sig1, ..., signal sign)``: Transmit the real component of the supplied  ``signals`` on a ``txchannel`` resource for a ``length`` of time. Advances the real-time clock of this channel by ``duration``.
When multiple signals are supplied they are ``mix``ed together.

Channel signal input operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``receive(rxchannel ch, length duration) -> signal``: Capture a real ``signal`` from a ``rxch`` for a ``length`` of time. Increments the target channel's clock by ``duration``. The produced signal's clock is shifted to ``time(ch)`` so as to demodulate the signal against the measurement carrier tone.

### Channel operations:
- ``time(channel ch) -> time`` - Reference to the current real clock-time of the channel.
- ``barrier(channel ch1, ..., channel chn)`` - Advance the real clocks of each input channel to ``max(time(ch1), ..., time(chn))``.
- ``delay(channel ch, length duration)`` - Increment the real signal clock by a duration.

### Channel Getters
The following operations are supported to fetch the configured channels for the specific device.
- ``txch(qubit q0, ..., qubit qn, str name) -> txchannel``
- ``rxch(qubit q0, ..., qubit qn, str name) -> rxchannel``

Alternatively, one could declare a channel of a given name directly and rely on the compiler to bind this to a physical channel on the device by the declared name.

.. code-block: none

  txchannel d0


Frames
------

It turns out to be quite useful to keep track of a set of carrier signals
throughout the execution of a program. These carrier signals are called "frames"
and are defined by :math:$A*e^{i\left(2\pi f t + \theta\right)}$, where `f` is
frequency, `theta` is phase, and `A` is a scaling factor. Frames will also track
time appropriately so programs do not need to deal in absolute time. The
canonical motivation for keeping track of phase is to implement a "virtual
Z-gate", which does not require a physical pulse but rather shifts the phase of
all future pulses on that frame.

The ``frame`` type is a compile-type type representing a *reference* to a frame.
The frame is composed of four parts:

1. A frequency ``frequency`` of type ``float``. It is not initialized and must
be set before any pulses can be played on that frame.
2. A phase ``phase`` of type ``angle``. This is initialized to the value 0.
3. An amplitude ``scale`` of type ``float``. This is initilized to the value 1.0.
4. A time of type ``dt`` which is manipulated implicitly and cannot be modified
other than through existing timing instructions like ``delay`` and ``barrier``.

The exact precision of these parameters is hardware specific.

frameof command
~~~~~~~~~~~~~~~

Frames are uniquely identified by a string name and a set of qubits. The order
of qubits does not matter.

Frames are retrieved using the ``frameof`` function and passing in the name and
list of physical qubits.

.. code-block: none

   frameof("drive", %0)

   // These next two lines refer to the same frame
   frameof("coupling", %0, %1)
   frameof("coupling", %1, %0)

Frame names may seem like they ascribe meaning or that there are only certain
permissable names. This is not the case; frame names are arbitrary. The frames
are later mapped to channel names that do have meaning for a certain hardware
vendor. For example, the hardware vendor may choose to map frames to channels
using JSON:

.. code-block: javascript

   {
     drive: {
       "{0}": "channel0",
       "{1}": "channel1"
     coupling: {
       "{0,1}": "channel2"
     }
   }

This has the advantage that one can run any program with any arbitrary frame
names provided a mapping to the appropriate channels is given.

Restrictions on the use of frames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two important considersations when dealing with frames.

First, frames are compile time constants. Runtime variables cannot be used as
arguments to frames; the frame must be resolvable at compile time. This also
means that assigning a frame to an alias (for the purpose of avoiding typing)
needs to be done with ``const`` not ``let``.

.. code-block: none

   const driveframe = frameof("drive", %0);

Second, frames return references not values. This means that calling the same
``frameof`` command in different places is the same as assigning the frame to a
constant and referencing it multiple times.

Frame manipulation
~~~~~~~~~~~~~~~~~~

The (frequency, phase, scale) of a frame can be manipulated throughout program
by referencing ``.frequency``, ``.phase``, and ``.scale``. Operations must be
appropriate for the respective type, ``float`` for frequency, ``angle`` for
phase, and ``float`` for scale. Again, the exact precision of these calculations
is hardware specific.

Here's an example of manipulating the phase to calibrate an ``rz`` gate:

.. code-block:: none

   // Shift phase of qubit 0's "drive" frame by pi/4, eg. an rz gate with angle -pi/4
   frameof("drive", %0).phase += pi/4;

   // Equivalent
   const drive = frameof("drive", %0);
   drive.phase += pi/4;

   // Define a calibration for the rz gate on all physical qubits
   defcal rz(angle[20]:theta) %q {
     frameof("drive", %q).phase -= theta;
   }

Here's an example qubit spectroscopy experiment.

.. code-block:: none

   qubit q;

   const shots = 1000;
   const start = 5e9; // 5 GHz
   const end = 6e9; // 6 GHz
   const points = 50;

   complex[32] iq, average;
   complex[32] output[points];

   const driveframe = frameof("drive", q);

   for p in [0 : points-1] {
     // The key line: pick the frequency to sample
     driveframe.frequency = start + (end-start) * p / points;
     output[p] = 0;

     for i in [0 : shots-1] {
       // Assumes suitable calibrations for reset, x, and measure_iq
       // and that the x gate references the same "drive" frame
       reset q;
       x q;
       measure_iq q -> iq;

       output[p] = (output[p] * i + iq) / (i + 1);
     }
   }

Manipulating frames based on the state of other frames is also permitted:

.. code-block:: none

   // Swap phases between two frames
   const temp = frame1.phase;
   frame1.phase = frame2.phase;
   frame2.phase = temp;

Pulses
------

Pulses have two representations:

- An array of complex samples which define the points for the pulse envelope
- A``pulse`` type, which describes an abstract mathematical function
  representing a pulse. This will later be materialized into a list of complex
  samples, either by the compiler or the hardware using the parameters provided
  to the pulse template.

A value of type ``pulse`` is retrieved by calling one of the built-in pulse
template functions. Note that each of these functions takes a type ``length``
as a first argument, since pulses need to have a definite length. Using the
hardware dependent ``dt`` unit is recommended, since the compiler may need to
down-sample a higher precision pulse to physically realize it.

.. code-block:: none

   // amp is pulse amplitude at center
   // center is the mean of pulse
   // sigma is the standard deviation of pulse
   gaussian(length:l, complex[float[32]]:amp, length:center, length:sigma)

   // amp is pulse amplitude at center
   // center is the mean of pulse
   // sigma is the standard deviation of pulse
   sech(length:l, complex[float[32]]:amp, length:center, length:sigma)

   // amp is pulse amplitude at center
   // center is the mean of pulse
   // square_width is the width of the square pulse component
   // sigma is the standard deviation of pulse
   gaussian_square(length:l, complex[float[32]]:amp, length:center, length:square_width, length:sigma)

   // amp is pulse amplitude at center
   // center is the mean of pulse
   // sigma is the standard deviation of pulse
   // beta is the Y correction amplitude, see the DRAG paper
   drag(length:l, complex[float[32]]:amp, length:center, length:sigma, float[32]:beta)

   // Define a constant pulse of length l
   constant(l:length)

Play instruction
----------------

Pulses are scheduled using the ``play`` instruction. These instructions may
only appear inside a ``defcal`` block!

Play instructions have two required parameters:

- a value of type ``pulse`` representing the pulse envelope
- the frame to use for the pulse

.. code-block:: none

   // Play a 3 sample pulse on qubit 0's "drive" frame
   play([1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j]) frameof("drive", %0);

   // Play a gaussian on qubit 1's "drive" frame
   frame f1 = frameof("drive", %1);
   play(gaussian(...)) f1;

Capture Instruction
-------------------

Acquisition is scheduled by a ``capture`` instruction. This is a special
``kernel`` function which is specified by a hardware vendor. The measurement
process is difficult to describe generically due to the wide variety of
hardware and measurement methods. Like the play instruction, these instructions
may only appear inside a ``defcal`` block!

The only required parameter is a ``frame``.

The following are possible parameters that might be included:

- A "duration" of type ``length``, if it cannot be inferred from other parameters
- A "filter", which is dot product-ed with the measured IQ the distill the
  result into a single IQ value
- A "tag", which could be used to identify which branch of an if statement was
  traversed

Again it is up to the hardware vendor to determine the parameters and write a
kernel definition at the top-level, such as:

.. code-block:: none

   // Minimum requirement
   kernel capture(frame output) -> complex[32];

   // A capture command with more features
   kernel capture(frame output, pulse filter) -> complex[32];

The return type of a ``capture`` command varies. It could be a raw trace, ie. a
list of samples taken over a short period of time. It could be some averaged IQ
value. It could be a classified bit. Or it could even have no return value,
pushing the results into some buffer which is then accessed outside the program.

Timing
------

Each ``channel`` maintains its own "clock". When a pulse is played the clock for
that channel advances by the length of the pulse.

For channels, everything behaves analogous to qubits in the
`Delays <delays.html>`_ section of this specification. There are however some
small differences.

The ``delay`` instruction may take a channel instead of a qubit. The ``barrier``
instruction may also take a list of channels instead of a list of qubits.

``defcal`` blocks have an implicit barrier on every channel used within the block,
meaning that clocks are guaranteed to be aligned at the start of the block.
These blocks also need to have a well-defined length, similar to the ``boxas``
block.

.. code-block:: none

   signal pulse = ...; // some 100dt pulse

   defcal simultaneous_pulsed_gate %0 {
     transmit[100dt] txch("drive0", %0), pulse;
     delay[20dt] txch("drive1", %0);
     // Starts the 100dt pulse 20dt into "drive0" already playing it
     // But transmits only the first 80 samples so as to end at the
     // same time.
     transmit[80dt] txch("drive1", %0), pulse;;
   }


Examples
--------

Cross-resonance like gate
~~~~~~~~~~~~~~~~~~~~~~~~~
Playing simultaneous pulses on two separate channels with a shared phase/frequency relationship.
Demonstrating the ability to express the semantics required for the cross-resonance gate.

.. code-block: none
  // Initialize
  let d0 = txch(0, "drive");
  let d1 = txch(1, "drive");
  let carrier = exp(1.0, 5e9, 0);
  // Do a bunch of operations incrementing the channels times.
  // Synchronize clocks.
  barrier(d0, d1);
  let wf2 = gaussian_square(1., 1024dt, 32dt, 128dt);;
  let wf2 = gaussian_square(0.1, 1024dt, 32dt, 128dt);
  // Produce new carrier with phase shifted from derived
  let offset_carrier = phase(carrier, pi/2);
  tx(d0, mix(wf1, carrier), 1024dt);
  tx(d1, mix(wf2, pi2_offset_carrier), 1024dt);


Measuring a qubit
~~~~~~~~~~~~~~~~~

Here we use a kernel operation on the signal to discriminate the signal to a bit.

.. code-block: none

  kernel discriminate(sig: signal, len: length, time: length) -> bit;
  let m0 = txch(0, "measure");
  let cap0 = rxch(0, "capture");

  // Force time of carrier to 0 for consistent phase for discrimination.
  let carrier = set(exp(1.0, 5e9, 0), 0);
  barrier(q0, cap0);
  tx(m0, mix(carrier, gaussian_square(1.0, 16000dt, 262dt, 13952dt)));
  // Measure and demodulate measured signal.
  let output = mix(rx(cap0, 16000dt), phase(carrier, pi));
  // Pass signal to kernel to be discriminated.
  let result: bit = discriminate(output, 16000dt);

Clocking example
~~~~~~~~~~~~~~~~

.. code-block: none

  let d0: txchannel; // t=0
  let d1: txchannel; // t=0

  let env0: envelope = [0.0, 1.0, 0.0];
  let carrier: wave = carrier(1.0, 5e9, 0.0);

  let sig0: signal = mix(env0, carrier);
  //        env0[t=0] carrier[t=0]
  //             \     /
  //                |
  //              mix[t=0]
  //                |
  //              sig0[t=0]

  let sig1: signal = shift(sig0, 10);
  //        env0[t=0] carrier[t=0]
  //             \     /
  //                |
  //              mix[0]
  //                |
  //            shift(10)[0]
  //                |
  //              sig1[t=0]

  // Advance physical channel clock by transmitting instruction
  tx(d0, sig0, 3); // t=0->3
  //    env0[t=0->3] carrier[t=0->3]
  //             \     /
  //                |
  //            mix[t=0->3]
  //                |
  //            sig0[t=0->3]

  // Envelope has clock forced to t=0
  tx(d0, sig0, 3); // t=3->6
  //    env0[t=0->3] carrier[t=3->6]
  //             \     /
  //                |
  //            mix[t=3->6]
  //                |
  //            sig0[t=3->6]

  // Inheritance of clock shift in signal
  tx(d0, sig1, 10); // t=3->6
  //    env0[t=0->10] carrier[t=16->26]
  //             \     /
  //                |
  //            mix[t=16->26]
  //                |
  //            shift(10)[t=16->26]
  //                |
  //              sig1[t=6->16]

  // Channel d1's clock has not yet advanced.
  // This enables scheduling in parallel across channels.
  tx(d1, sig0, 3); // t=0->3
  //    env0[t=0->3] carrier[t=0->3]
  //             \     /
  //                |
  //            mix[t=0->3]
  //                |
  //            sig0[t=0->3]

