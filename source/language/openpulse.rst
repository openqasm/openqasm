.. role:: raw-latex(raw)
   :format: latex
..

OpenPulse Grammar
=================

OpenQASM allows users to provide the target system's implementation of quantum operations with
``defcal`` `blocks <pulses.rst>`_ . Calibration grammars are open to extension for system
implementors. In this document, we outline one such grammar, OpenPulse, which maybe selected
within a supporting compiler through the declaration `defcalgrammar "openpulse" <VERSION>`.

This grammar is motivated by the original OpenPulse specification, a JSON wire-format for
pulse-level quantum programs defined in the paper
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment <https://arxiv.org/abs/1809.03452>`_.
The textual format described here has several advantages over the original JSON format:

- Improved readability
- Pulse timing is based on instruction ordering and works with programs containing branching control flow
- Reusable gate calibrations enable more succinct calibration descriptions.
- Pulse definitions are declared as a calibration for individual circuit instructions attached to physical qubits enabling the microcoding of gate level operations.
- Richer ability to compose complex pulses through natural DSP-like operations.
- Clearly defined relationship between pulses, channels and the phases of compilation to hardware resources.
- Use of multiple oscillators on a single channel at the same time (see :ref:`Geo Gate`):

Openpulse provides a flexible programming model that should extend to many quantum control schemes and hardware.
At the core of the OpenPulse grammar are the concepts of ``signals`` and ``channels``. Many of these concepts
are inspired by the signal processing language <Faust `https://faust.grame.fr/`>_.
``Signals`` define a discrete set of samples (or waveform) which are then played or captured via a
a ``channel`` on the target device. A channel is a software abstraction which
allows the programmer to be agnostic to complexities of the device's underlying pulse generation
hardware. It is the responsibility of the target device's compiler to map ``signals``
to the applied channels in target hardware.

**NOTE: We assume we have arrays defined with a [...] symtax and complex[size] types.**

Signals
-------

A ``signal`` is a generalized concept of a ``pulse``. A signal is a discrete, time-dependent function
:math:`s(t): ℤ->ℂ`. The input time is an integer representing the number of elapsed samples. It can
be viewed as the "index" into the signal. In hardware, the time :math:`t_h`, is given by
:math:`t_h=t*dt`, where ``dt`` is the time elapsed per sample. Signals have a max unit-norm
(signal processes that emit a signal outside of this range clip).

All signals have a ``.duration`` property giving the length of the signal.

.. code-block:: c

    signal sig = [0.1, 1.+1I, 0.1 - 0.2I];
    int[32] x = sig.duration + 1;  // x is 4

Signals are produced from two fundamental types, ``envelopes`` and ``carriers``.

Envelopes
~~~~~~~~~

Envelopes are discrete waveforms :math:`f(t), ℤ->ℂ`. Examples include a waveform described as
an array of complex samples or a parametric function supported directly by the hardware
such as a Gaussian waveform.

Arrays initialization is done as in OpenQASM.

.. code-block:: c

    envelope env = [0.1, 1.+1I, 0.1 - 0.2I, ...];

Parametric pulses are initialized by assigning the result of``envelope``'s to the result of a (kernel) function call.

.. code-block:: c

  envelope env = gaussian(1.+1I, 1024dt, 128dt);

The following parametric functions are currently defined

.. code-block:: c

    kernel gaussian(complex[size] amp, length duration, length sigma) -> envelope;
    kernel gaussian_square(complex[size] amp, length duration, length sigma, length square_width) -> envelope;
    kernel drag(complex[size] amp, length duration, length sigma, float[size] beta) -> envelope;
    kernel constant(complex[size] amp, length duration) -> envelope;

Carriers
~~~~~~~~

Carriers represent stateful modulation signals in hardware such as those used to implement the <Virtual Z-gate `https://arxiv.org/abs/1612.00858`>_.
The standard carrier has the form :math:`Ae^{i(2*\pi*\imag*freq(t_i)*\Delta t +\phi(t_i) + \phi(t_{i-1})}`.
:math:`A` is the amplitude. :math:`freq(t_i)` and :math:`\phi(t_i)` are the carrier's instantaneous frequency and
relative phase respectively, and :math:`phi(t_{i-1})` is the carrier's accumulated phase which stores the history of the carrier.
Carriers are declared by calling an exponential kernel function
``kernel exp(complex[size] amp, float[size] freq, angle[size] phase) -> carrier``.

.. code-block:: c

    carrier carr = exp(0.5+0.5I, 5e9, pi);

The instantaneous carrier parameters may be accessed via ``carrier.amp``, ``carrier.freq`` and ``carrier.phase``.
Standard OpenQASM assignment and arithmetic operations apply to these fields--for instance,
to increment the phase one may apply ``carrier.phase += pi;``. However, in contrast to the circuit model,
care must be taken to the global time :math:`t_i` at which this phase increment occurs, as a carrier may
be shared across many channels operating in parallel in time. Updates to carriers take place at the
greatest time of all channels within the current scope. This enables reasoning about the absolute accumulated
phase of the carrier and how this impacts signals that are emitted on different channels with a shared carrier.
See the :ref:`Timing` for more detail on this behavior.

It is the responsibility of the compiler to identify operations which affect the carrier state, and the
relative timing at which the update takes place with respect to the target channel.

Signal composition & transformation operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complex signals may be constructed through signal transformation and composition operations applied to
``envelope`` and ``carrier`` signals which are the signal production base types. This is very natural
within the OpenPulse DSP-like formalism. As a simple example, consider a signal which is the sum of
two Gaussian envelopes, modulated by two carriers which have a phase differing by a factor of 2.

.. code-block:: c

    envelope env = gaussian(...);
    carrier carr = exp(...);
    signal pi2_carr = phase(carr, pi/2);
    signal sig = sum(mix(env, carr), mix(env, pi2_carr));

Each operation takes as input one or more signals (which can also be ``envelope`` or ``carrier``)
applies a transformation, and produces a new signal. Note these do not mutate the input signals, but
instead pipe the signal into a transfer function producing a new signal derived from the inputs.
Signals are classical and may be reused. It is the responsibility of the target compiler to decided
how to implement signals on hardware. For example, the compiler may implement carriers by applying a
digital sideband to supplied envelopes and tracking all phases in software or alternatively it may
assign carriers directly to <numerically controlled oscillators `https://en.wikipedia.org/wiki/Numerically-controlled_oscillator`>_
in control hardware.

Currently, the following signal operations exist:

.. code-block:: c

    shift(signal sig, length time) -> signal  // Shift signal by ``time``, :math:`s(t)->s(t+time)`
    set(signal sig, length time) -> signal  // Force the signal to begin at ``time``

    // Mix ``n`` input signals to produce a new signal. This is equivalent to the product signal
    // :math:`s(t_i) = s_1(t_i)*s_2(t_i)* ... *s_n(t_i)`.
    mix(signal sig0, signal sig1, ..., signal sig_n) -> signal

    // Add ``n`` input signals sample by sample to produce a new signal. This is equivalent to
    // :math:`s(t_i) = s_1(t_i)+s_2(t_i)+ ... +s_n(t_i)`.
    sum(signal sig0, signal sig1, ..., signal sig_n) -> signal

    // Construct a signal as a piecewise function w/ ``sig0, t <= time`` and ``sig1, t > time``
    piecewise(signal sig0, signal sig1, length time) -> signal

    offset(signal sig, complex[size] val) -> signal  // Add ``val`` to every sample, :math:`s(t)->val+s(t)`
    scale(signal sig, complex[size] val) -> signal  // Scale input signal by ``val``, :math:`s(t)->val*s(t)`
    conj(signal sig) -> signal  // Take the complex conjugate of the input signal
    re(signal sig) -> signal  // Take the real component of the input signal
    im(signal sig) -> signal  // Take the imaginary component of the input signal

    // Compute the norm of the signal, :math:`|s(t)| = \sqrt{\sum{|s(t_i)|^2}}`, where the square of
    // the sample norm is the sum of squares of the real and imag components of the sample.
    abs(signal sig) -> signal

    phase(signal sig, angle[size] ang) -> signal  // Modulate signal w/ relative phase, :math:`s(t)->s(t)*e^{\imag*ang}`

Signal Networks
~~~~~~~~~~~~~~~

As described above, signals may be composed via transformation functions to form new signals that are derived from the input parent signals. For example ``new_signal = mix(env, carr);``
produces a new child signal that is a mixture of its parent envelope and carrier wave signals. Combining signals in this way forms a "signal network", where signals are
edges between signal production/transformation nodes. A signal network has a correspondence with a traditional microwave block diagram. Within the signal programming model,
signals are constructed via composition. Signals are emitted to the physical world by transmitting them on a ``channel``.
Within this formalism, ``envelopes`` and ``carriers`` are *source* nodes that produce a new signal (ie., no input edges).

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
In practice, we allow reusing the named edges without requiring an explicit split operation.

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

The signal network may enable the compiler to restructure the signal in a way that better maps to available hardware.
For example, if the hardware is capable of providing support for a ``carrier``, it may natively represent a signal of the form ``mix(envelope, carrier)``.
Otherwise it may choose to rewrite the signal as a sidebanded envelope. Critically, compilation from the high-level programmer's perspective to the low-level
hardware implementation of an OpenPulse program may be performed within the same representation.

Channels
--------

Channels model hardware resources which can play signals to manipulate a qubit
or capture a signal emitted from the target system such as a qubit measurement result.

Within the OpenPulse grammar channels have two critical responsibilities:

1. They are the interface between connecting ``signal``'s (and correspondingly gates)
to configured control hardware in the target system, ie., they are the
representations of the system IO ports.
2. They are responsible for representing the instantaneous *time* of each HW resource
within a program's execution with respect to the global program time. As instructions are applied to the channel this clock is
incremented. As each channel maintains its own clock, it is possible to apply instructions sequentially
to channels and have the resulting ``signal``s be emitted in parallel at runtime. In this way channels
are similar to ports in an HDL language.

There is a many-to-many relationship between qubits and channels.
One qubit may be controlled by multiple channels.
Signals applied on different channels have different physical interactions with that qubit.
Inversely, a channel may also affect many qubits. For instance,
a channel could manipulate the coupling between two neighboring qubits, or
could even reference multiple qubits coupled in a chain.

Channels are defined by each vendor for every target system. It is expected that vendors
of quantum hardware provide the appropriate channel names and qubit mappings
as configuration information to end users.

There are two kinds of channels:

- transmit channels (``txchannel``): For emitting a ``signal`` to an output port of the quantum control system.
- receive channels (``rxchannel``): For capturing an input ``signal`` into the quantum control system.

To play a signal on a transmit channel for a given period of time,  the ``transmit`` instruction is used.

.. code-block:: c

    transmit(txchannel ch, signal sig, length duration)

``transmit`` increments the target channel's clock by ``duration``.

If ``envelope``'s and ``carrier``'s are signal ``sources``, the ``transmit`` operation is the signal ``sink`` (ie., it has no output edges).
It pipes the signal out of the OpenPulse domain into the physical hardware.

To capture a signal from a ``rxchannel``, the ``receive`` instruction is used.

.. code-block:: c

    receive(rxchannel ch, length duration) -> signal  // raw signal data

The ``receive`` instruction returns raw signal output. If you wish to get a higher level of data, processing
functions such as ``kernel``'s or ``discriminator``'s must be applied. For transmon systems, there are three
data levels which may be obtained as follows:

- Level 0: The raw input signal - ``receive(rxchannel ch, length duration) -> signal``.
- Level 1: A single IQ value derived from the signal after the application of a filter and integration kernel - ``kernel my_kernel(signal input) -> complex[64]  // IQ data``
- Level 2: A single bit produced by thresholding the level 1 output - ``kernel discriminate(complex[64] input) -> bit``. This typically is the final result produced and
    returned by ``defcal measure $q -> bit``.

``receive`` increments the target channel's clock by ``duration``.

Channel operations
~~~~~~~~~~~~~~~~~~

Channels provide several operations such as ``barrier`` and ``delay`` to enable synchronization of the channels
within a program:

.. code-block:: c

    // Synchronize the clocks of all input channels. This is performed by advancing the clocks to
    // maximum time across all input channels.
    barrier(channel ch1, ..., channel chn)

    // Barrier all channels on the device
    barrier_all()

    // Increment the clock of the input channel by ``duration``
    delay(channel ch1, length duration)

Channel accessors
~~~~~~~~~~~~~~~~~~

As noted, the hardware vendor for a given device is responsible for providing information necessary
to access the channels.

This should be done by providing a mapping between a qubit list + name and the configured hardware channel.
The hardware can then be accessed as OpenPulse ``txchannel``/``rxchannel``'s via "get" functions.

.. code-block:: c

    txch(qubit q0, ..., qubit qn, str name) -> txchannel  // get transmit channel
    rxch(qubit q0, ..., qubit qn, str name) -> rxchannel  // get receive channel

The qubits must be **physical** qubits. Furthermore, ordering of qubits is important. For instance,
``txch($0, $1, "control")`` and ``txch($1, $0, "control")`` may be used to implement distinct cross-resonance
gates. It is also possible to access a channel by its full name, without supplying any qubits, if that has between
implemented by the vendor. For instance, ``txch("<channel_name>")`` may refer to a transmit channel with an arbitrary name.

.. code-block:: c

    txchannel d0 = txch($0, "drive");  // channel for driving at qubit $0's freq
    txchannel cr1_2 = txch($1, $2, "coupler");  // channel for a coupler between two qubits
    txchannel m2 = txch($2, "measure");  // channel for transmitting measurement stimulus

    // capture channels for capturing qubits $0 and $1
    rxchannel cap0 = rxch($0, "capture");
    rxchannel cap1 = rxch($1, "capture");

Examples
---------

Cross-resonance gate
~~~~~~~~~~~~~~~~~~~~

Playing simultaneous pulses on two separate channels with a shared phase/frequency relationship.
Demonstrating the ability to express the semantics required for the cross-resonance gate.

.. code-block:: c

    defcal cx $0, $1 {
        // Initialize
        txchannel d0 = txch($0, "drive");
        txchannel d1 = txch($1, "drive");

        envelope env0 = gaussian_square(1., 1024dt, 32dt, 128dt);
        envelope env1 = gaussian_square(0.1, 1024dt, 32dt, 128dt);

        carrier qubit_carrier = exp(1.0, 5e9, 0);

        // Previous operations incrementing channels to unknown times

        // Synchronize clocks.
        barrier(d0, d1);

        // Phase update for virtual-Z gate
        carr.phase += pi/2;

        // Do pre-rotation
        // {...}

        // Use common carrier, w/ latter phase shifted by pi/2
        transmit(d0, mix(env0, carr), 1024dt);
        transmit(d1, mix(env0, phase(carr, pi/2)), 1024dt);

        // Do post-rotation
        // {...}
    }

.. _Geo Gate:

Single qubit geometric gate
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Take qubit from ``|0>`` to ``|2>`` state with a single composite pulse. This requires
emitting a signal with multiple carriers simultaneously on a common channel. For further background see
`here <https://www.nature.com/articles/nature12010>`_.

.. code-block:: c

    defcal geo_gate(angle[32] theta) $q {
        // theta: rotation angle (about z-axis) on Bloch sphere

        // Assume we have calibrated 0->1 pi pulses and 1->2 pi pulse envelopes (no sideband)
        envelope X_01 = {...};
        envelope X_12 = {...};

        // Get 0->1 freq and 1->2 freq for $q
        float[64] fq_01 = 5e9;
        float[64] fq_12 = 5.3e9;

        float[64] a = sin(theta/2);
        float[64] b = sqrt(1-a**2);

        // pi geo pulse envelope is: :math:`a*X_01 + b*X_12`
        carrier carr_01 = exp(a, fq_01, 0);
        carrier carr_12 = exp(b, fq_12, 0);

        signal geo_pi = sum(mix(X_01, carr_01), mix(X_12, carr_12));

        tx_channel dq = txch($q, “drive”);
        // play back to back geo pi pulses to get full 2pi state transfer
        transmit(dq, geo_pi, geo_pi.duration);
        transmit(dq, geo_pi, geo_pi.duration);
    }

Neutral atoms
~~~~~~~~~~~~~

This example demonstrates a Hahn echo and Ramsey sequence in a system of neutral atoms. Neutral atoms
encode qubit states in the electron levels of an atom and are typically controlled via laser light. This
example is roughly based off the work in <Levine et al https://arxiv.org/pdf/1908.06101.pdf>_. The signal chain
is composed of two electro-optic modulators (EOM) and an acousto-optic deflector (AOD). The EOMs
sideband the laser light while the AOD diffracts light in an amount proportional to the frequency of the drive stimulus.
We apply a Hahn echo to qubit 1 and Ramsey sequence's to qubits 2, 3. The example demonstrates phase tracking
requirements amongst carriers, frequency modulation and complex signal composition.
[**This example should be reviewed--also is it too complex/specific?**]

.. code-block:: c

    defcal neutral $1, $2, $3 {
        // Define the channels
        txchannel eom_a = txch($1, $2, $3, "eom_a");
        txchannel eom_b = txch($1, $2, $3, "eom_b");
        txchannel aod = txch($1, $2, $3, "aod");

        // Define the EOM signals, generated by Raman lasers. The Raman signals are detuned by an
        // amount Δ between the 5S1/2 to 5P1/2 transition. They are offset from each other by the
        // qubit frequency.
        float[64] Δ = ...;  // 5S1/2->5P1/2 detuning
        float[64] qubit_freq = ...;  // frequency of neutral atom qubit
        carrier raman_a = exp(..., Δ, 0.0);
        carrier raman_b = exp(..., Δ-qubit_freq, 0.0);

        // Three qubit carriers to track phase of each qubit
        // All neutral atom qubits have same frequency
        carrier q1_carr = exp(1.0, qubit_freq, 0);
        carrier q2_carr = exp(1.0, qubit_freq, 0);
        carrier q3_carr = exp(1.0, qubit_freq, 0);

        // Define pi/2 gaussian envelope
        length pi2_time = ...;  // qubit pi/2 pulse time
        pi2_sig = gaussian(..., pi2_time, ...);

        // Sideband-signal construction for the AODs to hit to target the qubit position. We use ``set`` to
        // re-zero the phase after every usage so as to avoid propagating the phase.
        float[64] q1_pos_freq = ...;
        float[64] q2_pos_freq = ...;
        float[64] q3_pos_freq = ...;

        q1_pos_sig = set(carrier(1.0, q1_pos_freq-qubit_freq, 0), 0);
        q2_pos_sig = set(carrier(1.0, q2_pos_freq-qubit_freq, 0), 0);
        q3_pos_sig = set(carrier(1.0, q3_pos_freq-qubit_freq, 0), 0);

        // Signals for AODs. We scale the amplitudes to reach a common Rabi rate for all the tones.
        complex[64] q1_pi2_amp = ...;
        complex[64] q2_pi2_amp = ...;
        complex[64] q3_pi2_amp = ...;

        q1_pi2_sig = scale(mix(q1_carr, q1_pos_sig, pi2_sig), q1_pi2_amp);
        q2_pi2_sig = scale(mix(q2_carr, q2_pos_sig, pi2_sig), q2_pi2_amp);
        q3_pi2_sig = scale(mix(q3_carr, q3_pos_sig, pi2_sig), q3_pi2_amp);

        // Loop over delay times from ``0`` to ``T``
        length T = ...;
        int[32] steps = ...;
        length inc_time = T/steps;
        for τ in [0:inc_time:T]:
            // Simultaneous π/2 pulses
            transmit(eom_a, raman_a, pi2_time);
            transmit(eom_b, raman_b, pi2_time);
            transmit(aod, sum(q1_pi2_sig, q2_pi2_sig, q3_pi2_sig), pi2_time);

            // Delay each channel
            delay(eom_a, eom_b, aod, τ/2);

            // π pulse on qubit 1 only -- composed of two π/2 pulses (for Hahn echo)
            for i in [0:2] {
                transmit(eom_a, raman_a, pi2_time);
                transmit(eom_b, raman_b, pi2_time);
                transmit(aod, q1_pi2_sig, pi2_time);
            }

            // Delay each channel again
            delay(eom_a, eom_b, aod, τ/2);

            // Phase shift the signals by diff amounts
            float[64] tppi_1 = ...;
            float[64] tppi_2 = ...;
            float[64] tppi_2 = ...;
            q1_carrier.phase += tppi_1 * τ;  // autocast to angle[size]
            q2_carrier.phase += tppi_2 * τ;
            q3_carrier.phase += tppi_3 * τ;

            // Simultaneous π/2 pulses
            transmit(eom_a, raman_a, pi2_time);
            transmit(eom_b, raman_b, pi2_time);
            transmit(aod, sum(q1_pi2_sig, q2_pi2_sig, q3_pi2_sig), pi2_time);
    }

Measurement
~~~~~~~~~~~

Demonstrates how to define a measurement of a superconducting qubit through a dispersive readout
process within the signal framework.

.. code-block:: c

    // Use a boxcar function to generate IQ data from raw signal
    kernel boxcar(signal input)->complex[64];
    // Use a linear discriminator to generate bits from IQ data
    kernel discriminate(complex[64] iq)->bit;

    defcal measure $0 -> bit {
        // Define the channels
        txchannel m0 = txch($0, "measure");
        rxchannel cap0 = rxch($0, "capture");

        // Force time of carrier to 0 for consistent phase for discrimination.
        signal carr = set(exp(1.0, 5e9, 0), 0);

        // Apply measurement stimulus
        envelope meas_pulse = gaussian_square(1.0, 16000dt, 262dt, 13952dt);

        // Transmit signal
        transmit(m0, mix(carrier, meas_pulse), meas_pulse.duration);
        // Align measure and capture channels
        barrier(m0, cap0);
        // Capture transmitted signal after interaction with measurement resonator
        signal raw_output = receive(cap0, meas_pulse.duration);

        // Kernel and discriminate
        complex[32] iq = boxcar(raw_output);
        bit result = discriminate(iq);

        return result;
    }

Rz gate (Virtual-Z Gate)
~~~~~~~~~~~~~~~~~~~~~~~~

Demonstrates how to implement an Rz gate (e.g. Virtual-Z gate) with signals.

.. code-block:: c

    defcal rz(angle[20] theta) $q {
        txchannel dq = txch("drive", $q);
        barrier dq;
        // Uses an undefined qubit attribution system.
        carrier qubit_carrier = get_attr("carrier", $q);
        qubit_carrier.phase += -theta;
    }

Qubit spectroscopy
~~~~~~~~~~~~~~~~~~

Construct a ``defcal`` for doing qubit spectroscopy. Finds the qubit's resonant frequency. This
example also demonstrates how ``defcal``'s can enable general calibration experiments. Note analysis
should be performed in a higher level language on the output data.

.. code-block:: c

    kernel boxcar(signal result) -> complex[64];

    const int[32] steps;
    const int[32] shots;

    input float[64] freq_low;
    input float[64] freq_high;
    output array[array[complex[64], shots], steps] result;

    defcal sp_cal(float[64] freq) $q -> complex[64] {
        txchannel dq = txch($q, "drive");
        rxchannel cap0 = rxch($q, "capture");

        envelope env = gaussian(0.3, 1024dt, 256dt);
        // Force phase to be the same regardless of time.
        carrier carr = set(exp(1.0, freq, 0.0), 0);

        transmit(dq, mix(env, carr), env.duration);
        barrier_all();  // sync clocks

        complex[64] iq = measure $q;  // precalibrated ``measure`` returning iq data
        return iq;
    }

    for s in [0:steps] {
        // Sweep freqs from ``freq_low`` to ``freq_high``
        float[64] curr_freq = freq_low + (freq_high-freq_low)*s/steps;
        // Fill the output iq array w/ freq sweep data
        output[s] = 0;
        for i in [0:shots] {
            output[s][i] iq = sp_cal(curr_freq) $q;
        }
    }

Clocking example
~~~~~~~~~~~~~~~~

Demonstrates how clocking works with shifting of signals across channels. The sample index ``t_i``
only changes when a signal is transmitted/received.

    .. code-block: c

        txchannel d0 = txch($0, "drive");
        txchannel d0 = txch($0, "drive");

        envelope env0 = [0.0, 1.0, 0.0];
        carrier carr0 = exp(1.0, 5e9, 0.0);

        // :math:`sig0=[0.0, 1.0, 0.0]*e^{2*\pi*i*5e8*t_i*dt}`
        signal sig0 = mix(env0, carrier);

        // :math:`sig1=[0.0, 1.0, 0.0]*e^{2*\pi*i*5e8*(t_i*dt+10dt)}`
        signal sig1 = shift(sig0, 10dt);

        // ``d0`` clock begins at ``t_i=0``
        // Advance ``d0`` clock by 3 samples
        // Uses sample indices ``t_i={0,1,2}``
        tx(d0, sig0, 3);

        // ``d0`` clock now at ``t_i=3``
        // Advance ``d0`` clock by 3 samples
        // Uses sample indices ``t_i={3,4,5}``
        tx(d0, sig0, 3);

        //  ``d0`` clock now at ``t_i=6``
        // Advance ``d0`` clock by 10 samples
        // Uses sample indices ``t_i={6,7,8,...,13,14,15}``
        tx(d0, sig1, 10);

        // ``d1`` clock has not yet advanced; starts at ``t_i=0``
        // Advance ``d1`` clock by 3 samples
        // Uses sample indices ``t_i={0,1,2}``
        // This enables scheduling in parallel across channels.
        tx(d1, sig0, 3);

.. _Timing:

Timing
------

Each ``channel`` maintains its own "clock". When a signal is transmitted/received, the channel clock
is played the clock for advances by the length of the signal (``signal.duration``).

``delay`` and ``barrier`` instructions in OpenPulse resolve timing as in the qubit case outlined in the
`Delays <delays.html>`_ section of the OpenQASM specification. At the pulse level, however,
``delay`` and ``barrier`` take ``channels`` as input, rather than qubits.

.. code-block:: c

    signal sig = ...; // some 100dt pulse

    defcal simultaneous_pulsed_gate $0 {
        txchannel d0 = txch($0, "drive");
        txchannel d1 = txch($1, "drive");
        // sig begins playing on ``d0``
        transmit(d0, sig, sig.duration);
        // Delay d1 by 20dt
        delay(d1, 20dt);
        // Next signal on ``d1`` will start at ``20dt``. We now play ``sig`` on ``d1``. It trails the
        // ``sig`` on ``d0`` by ``20dt``. We only play it on ``d1`` for ``80dt`` so it finishes at the
        // same time as ``d0``. Note that the full signal will play on ``d0``, but only the first 80
        // samples will play on ``d1``.
        transmit(d1, sig, sig.duration-20dt);
    }

``defcal`` blocks have an implicit barrier on every channel used within the block,
meaning that clocks are guaranteed to be aligned at the start of the block. Channel clock time persists
between ``defcal``'s within a common program, so the first use of channels within a ``defcal``
need not be at ``t=0``.

.. code-block:: c

    defcal cal1 $0, $1 {
        txchannel d0 = txch($0, "drive");
        txchannel d1 = txch($1, "drive");
        signal sig1 = ...;  // some 100dt pulse
        signal sig2 = shift(sig1, 20dt);  // shift to start at ``20dt``, length is only ``80dt``
        transmit(d0, sig1, sig1.duration);
        transmit(d1, sig2, sig2.duration);
    }

    defcal cal2 $0, $1 {
        txchannel d0 = txch($0, "drive");
        txchannel d1 = txch($1, "drive");
        signal sig3 = ...; // some 50dt pulse
        signal sig4 = ...; // some 75dt pulse
        transmit(d0, sig3, sig3.duration);
        transmit(d1, sig4, sig4.duration);
    }

    qubit $0;
    q0_cal1 $0;
    // Implicit barrier brings both clocks to ``100dt`` (``sig1.duration``) at start of ``q0_cal2``
    q0_cal2 $0;
    // Implicit barrier brings both clocks to ``175dt`` (``lengthof(q0_cal1)+sig4.duration``) at start of next ``defcal``

``defcal`` blocks must have a well-defined length for all possible input argument combinations and must be provided
to the scheduler at the circuit level.

It is critical that the update time of carrier properties be well-defined such that the appropriate absolute phase may be
accumulated. Updates of carrier properties are defined to occur at the maximum time across all channels used up to that point.

.. code-block:: c

    txchannel d0 = txch($0, "drive");
    txchannel d1 = txch($1, "drive");

    carrier carr0 = exp(1.0, 5e9, 0);
    carrier carr1 = exp(1.0, 5e9, 0);


    transmit(d0, carr0, 10dt); // Emit at 5GHz
    carr0.freq += 0.5e9; // occurs at t=10
    delay(d1, 20dt);
    carr1.freq += 1e9; // occurs at t=20

    barrier(d0, d1); // synchronize to t=20
    carr0.freq -= 0.5e9; // occurs at t=20 - absolute phase has accumulated of 2*pi*0.5e9*10*dt
    transmit(d0, carr1, 1000dt) // Emit at 6GHz
    transmit(d1, carr0, 1000dt) // Emit at 5GHz

Additional Considerations
-------------------------

- How do we handle ``defcal``'s that require classical input

For instance, spectroscopy as shown in the document requires a frequency input. Similarly, in a Rabi experiment,
an input amplitude will be needed for the drive pulse. I added a suggestion for generic ``defcal``'s,
which can take any classical parameter. But there are other options as well.

    - Create an attribute system which allows tagging of certain properties to a ``defcal``. This is along the lines of LLVM IR, for instance.
    - Allow global input from OpenQASM into ``defcal``'s.
    - Don't allow these advanced pulse experiments. The goal seems to be to move away from the pulse model, abstracting everything into circuits. Perhaps we don't want to support this functionality going forward.

- Reuse of channels, carriers, etc...

Since pulse syntax is local to ``defcal``'s, channels, carriers and signals have to be redefined within
each ``defcal``. It would be nice if we could define some global variables which could be shared across ``defcal``'s.
For instance, we would likely want to share a carreir containing a qubit's resonant frequency across
many ``defcals``'s. Some suggestions are below.

    - Include a global pulse namespace (or other initalization syntax). Something like

    .. code-block:: c

        // global variables to be used in any ``defcal``
        global "openpulse" {
            carrier c = exp(1.0, 5e9, 0);
            txchannel d0 = txch($0, "drive");
            rxchannel cap0 = rxch($0, "capture");
        }

    - Define namespaces where variables can be shared across ``defcal``'s as in C/C++
    - Include a global ``backend`` property, from which channels can be retrieved. Something like ``backend.get_tx_channel($0, "drive")``. For carriers, if the backend is capable of returning the resonant frequencies, that could be a good basis for prebuilt carriers likely to be reused.

- Syntactic sugar for ``signal`` operations. For instance, ``*`` instead of ``mix`` or ``+`` instead of ``sum``.
