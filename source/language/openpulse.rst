.. role:: raw-latex(raw)
   :format: latex
..

OpenPulse Grammar
=================

OpenQASM allows users to provide the underlying pulse definition for quantum gates
see `here <pulses.html>`_. This is done within ``defcal`` blocks. OpenQASM is can be used with any
well defined pulse grammar via the `defcalgrammar "name" VERSION` syntax. In this document, we
outline one such grammar, OpenPulse.

This grammar is motivated by the original OpenPulse specification, a JSON wire-format for
pulse-level quantum programs defined in the paper
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment <https://arxiv.org/abs/1809.03452>`_.
The textual format described here has several advantages over the JSON format:

- It is more readable
- Absolute time is handled through built-in timekeeping protocols
- Gates and classical instructions can be mixed in with pulses to create richer calibrations
- Pulse definitions are tied to circuit instructions rather than entire programs
- Richer ability to compose complex pulses via intuitive mathematical operations and a combination
  of envelopes and oscillators
- Ease of managing the relationship between pulses
- Use of multiple oscillators on a single channel at the same time (see geometric gates--LINK)

We aim to provide a flexible model that will cover the most extensive set of future scenarios. At
the core of the OpenPulse ``defcalgrammar`` are the concepts of ``signals`` and ``channels``.
``Signals`` define a discrete set of samples (or waveform) which are then played or captured via a
a *logical* ``channel`` on the target device. A *logical* channel is a software abstraction which
allows the programmer to be agnostic to complexities of the device's underlying pulse generation
hardware. It is the responsibility of the target device's compiler to map these *logical*
``signals`` to *physical* channels on the target hardware.

**NOTE: We assume we have arrays defined with a [...] symtax and complex[size] types.**

Signals
-------

A ``signal`` is a generalized concept of a `pulse`. A signal is a discrete, time-dependent function
:math:`s(t), ℤ->ℂ` defining the samples in a waveform. It is assumed to have max unit-norm. The time,
``t`` is given by :math:`t_i*dt`, where ``t_i`` is an integral sample number and ``dt`` is the time
elapsed per sample. ``t_i`` can be thought of as an "index" into the signal.

All signals have a ``.duration`` property giving the length of the signal.

.. code-block:: c

    signal sig = [0.1, 1.+1I, 0.1 - 0.2I];
    int[32] x = sig.duration + 1;  // x is 4

Signals are composed from two fundamental types, ``envelopes`` and ``carriers``.

Envelopes
~~~~~~~~~

Envelopes are discrete waveforms :math:`f(t), ℤ->ℂ`. This can be represented as an array of complex
samples or as a parametric pulse.

Arrays initialization is done as in OpenQASM.

.. code-block:: c

    envelope env = [0.1, 1.+1I, 0.1 - 0.2I, ...];

Parametric pulse initialization is done by assigning ``envelope``'s to the result of a (kernel) function call.

.. code-block:: c

  envelope env = gaussian(1.+1I, 1024dt, 128dt);

The following parametric functions are currently defined

.. code-block:: c

    kernel gaussian(complex[size] amp, length duration, length sigma) -> envelope;
    kernel gaussian_square(complex[size] amp, length duration, length sigma, length square_width) -> envelope;
    kernel drag(complex[size] amp, length duration, length sigma, float[size] beta) -> envelope;
    kernel constant(complex[size] amp, length duration) -> envelope;

Names of inputs are included to add clarity on what each argument represents.

Carriers
~~~~~~~~

Carriers are parametric functions represented by :math:`Ae^{i(2*\pi*\imag*freq*t+\phi)}`, where ``A``
is the amplitude, `freq` is the frequency and `phi` is the phase. Carriers are declared by calling
an exponential kernel function ``kernel exp(complex[size] amp, float[size] freq, angle[size] phase)``.

.. code-block:: c

    carrier carr = exp(0.5+0.5I, 5e9, pi);

The carrier parameters accessed by ``carrier.amp``, ``carrier.freq`` and ``carrier.phase``. Standard
operations apply to these fields--for instance, to increment the phase one can do ``carrier.phase += pi;``.

Carriers are local to individual ``defcal`` blocks. Phase aggregation will be tracked by the target's
compiler. This could be done by deconstructing signals on each ``txchannel``, identifying each carrier
declaration and writing a pass to aggregate phase on each of those carriers.

Signal composition operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A signal is built up through a host of transformations or compositions. The base types are
``envelope``'s and ``carrier``'s, which are transformed and combined into an arbitrarily complex
signal. As a simple example, one can consider a pulse which is the sum of two gaussians, modulated by
two carriers whose phases differ by a factor of 2.

.. code-block:: c

    envelope env = gaussian(...);
    carrier carr = exp(...);
    signal pi2_carr = phase(carr, pi/2);
    signal sig = sum(mix(env, carr), mix(env, pi2_carr));

Each operation takes as input one or more signals (which can also be ``envelope`` or ``carrier``)
applies a transformation, and produces a new signal. Note these do not mutate the input signals, but
are more akin to piping the signal into a transfer function. Signals are classical and may be copied
without a problem. It is up to the compiler to choose how to implement the required transformations
on hardware. Currently, the following signal operations exist

- ``shift(signal sig, length time)``: Shift the signal by ``time``, :math:`s(t)->s(t+time)`.
- ``set(signal sig, length time)``: Force the signal time index to begin at ``time``.
- ``mix(signal sig0, signal sig1, ..., signal sig_n) -> signal``: Mix ``n`` input signals to produce a new signal. This is equivalent to the product signal :math:`s(t_i) = s_1(t_i)*s_2(t_i)* ... *s_n(t_i)`.
- ``sum(signal sig0, signal sig1, ..., signal sig_n) -> signal``: Add ``n`` input signals sample by sample to produce a new signal. This is equivalent to :math:`s(t_i) = s_1(t_i)+s_2(t_i)+ ... +s_n(t_i)`.
- ``piecewise(signal sig0, signal sig1, length time) -> signal``: Construct a signal as a piecewise function w/ ``sig0, t <= time`` and ``sig1, t > time``.
- ``offset(signal sig, complex[size] val) -> signal``: Add ``val`` to every sample, :math:`s(t)->val+s(t)`.
- ``scale(signal sig, complex[size] val) -> signal``: Multiply each sample by ``val``, :math:`s(t)->val*s(t)`.
- ``conj(signal sig) -> signal``: The the complex conjugate of each sample.
- ``re(signal sig) -> signal``: Real component of input signal.
- ``im(signal sig) -> signal``: Imaginary component of input signal.
- ``abs(signal sig) -> signal``: Compute the norm of the signal->sqrt of sum of squares of each sample's norm.
- ``phase(signal sig, angle[size] ang) -> signal``: Modulate signal w/ phase, :math:`s(t)->s(t)*e^{\imag*ang}`.

Signal Networks
~~~~~~~~~~~~~~~

Signals may be composed via transformation functions to form new signals that are derived from the input parent signals. For example ``new_signal = mix(env, carr);``
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
Otherwise it may choose to rewrite the signal as a sidebanded envelope.

The signal network may also be useful in mapping carriers to the appropriate hardware units where phases can be tracked and aggregated properly.

Channels
--------

Channels map to hardware resources which can play signals to manipulate a qubit
or capture a signal after performing a measurement on a qubit.

Within the OpenPulse grammar channels have two critical responsibilities:

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

- transmit channels (``txchannel``): For emitting a ``signal`` to an output port on the quantum device (these manipulate the qubit state).
- receive channels (``rxchannel``): For capturing measurement output from a quantum device.

To play a signal on a transmit channel for a given period of time,  the ``transmit`` instruction is used.

.. code-block:: c

    transmit(txchannel ch, signal sig, length duration)

``trasnmit`` increments the target channel's clock by ``duration``.

If ``envelope``'s and ``carrier``'s are signal ``sources``, the ``transmit`` operation is the signal ``sink`` (ie., no output edges).
It pipes the signal out of the logical Openpulse domain into the physical hardware.

To capture a signal from a receive channel for a period of time, the ``receive`` instruction is used. There are
three output types for the receive function depending on the level of data the user wishes to obtain. There is ``signal``
output, which gives the raw signal obtained from the hardware. There is ``complex[32]`` output, which is the kerneled IQ data
resulting from the raw signal. And finally, there is `bit` output, which gives the discriminated binary value. Getting either IQ or
bit output will result in kerneling/discrimination being done in the hardware. If you wish to do this yourself, ``receive`` the raw
``signal`` and apply kernel functions for kerneling and discrimination (ie ``kernel IQ(signal raw)``, ``discriminate(complex[64] iq)``.

.. code-block:: c

    receive(rxchannel ch, length duration) -> signal  // raw signal data
    receive(rxchannel ch, length duration) -> complex[64]  // IQ data
    receive(rxchannel ch, length duration) -> bit  // bit data


``receive`` increments the target channel's clock by ``duration``. The produced signal is shifted
to ``time(ch)`` so as to demodulate the signal against the measurement carrier tone.

Channel operations
~~~~~~~~~~~~~~~~~~

.. code-block:: c

    barrier(channel ch1, ..., channel chn);  // Sync clocks of channel inputs
                                             // Advance clocks to maximum time across all channels
    barrier_all();  // Barrier all channels on the device
    delay(channel ch1, ..., channel chn, length duration);  // Increment clocks of each input channel by ``duration`` time

Channel accessors
~~~~~~~~~~~~~~~~~~

As noted, the hardware vendor for a given device is responsible for providing information necesssary
to access the channels.

This should be done by providing a mapping between a qubit list + name and the configured hardware channel.
The hardware can then be accessed as OpenPulse ``txchannel``/``rxchannel``'s via "get" functions.

.. code-block:: c

    txch(qubit q0, ..., qubit qn, str name) -> txchannel  // get transmit channel
    rxch(qubit q0, ..., qubit qn, str name) -> rxchannel  // get receive channel

The qubits must be **physical** qubits. Furthermore, ordering of qubits is important. For instance,
``txch($0, $1, "control")`` and ``txch($1, $0, "control")`` may be used to implement distinct cross-resonance
gates.

.. code-block:: c

    qubit $0, $1, $2;
    txchannel d0 = txch($0, "drive");  // channel for driving at qubit freq
    txchannel cr1_2 = txch($1, $2, "control");  // channel for CR gates-> drive at difference of ctrl/target freq
    txchannel m2 = txch($2, "measure");  // channel for measurement stimulus

    // capture channels for qubits $0, $1
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

        carrier carr = exp(1.0, 5e9, 0);

        // Do a bunch of operations incrementing the channels times.
        // Synchronize clocks.
        barrier(d0, d1);

        // Phase update some virtual Z gate
        carr.phase += pi/2;

        /*** Do pre-rotation ***/
        {...}

        // Use common carrier, w/ latter phase shifted by pi/2
        transmit(d0, mix(env0, carr), 1024dt);
        transmit(d1, mix(env0, phase(carr, pi/2)), 1024dt);

        /*** Do post-rotation ***/
        {...}
    }

Single qubit geometric gate
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Take qubit from ``|0>`` to ``|2>`` state with single pulse envelope. Requires different frequencies
played simultaneously on a common channel. Further background given
`here <https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/terra/qis_adv/single_qubit_geometric_gates.ipynb>`_.

.. code-block:: c

    defcal geo_gate(angle[32] theta) $q {
        // theta: rotation angle (about z-axis) on Bloch sphere

        // Assume we have calibrated 0->1 pi pulses and 1->2 pi pulse envelopes (no sideband)
        envelope X_01 = {...};
        envelope X_12 = {...};

        // Get 0->1 freq and anharmonicity for $q
        float[64] fq_01 = 5e9;  // hardcode or pull from some function
        float[64] anharm = 300e6;  // hardcode or pull from some function

        float[64] a = sin(theta/2);
        float[64] b = sqrt(1-a**2);
        // pi geo pulse envelope is: :math:`a*X_01 + b*X_12`
        // X_01 has freq fq_01
        // X_12 has freq fq_01+anharm
        carrier carr_01 = exp(a, fq_01, 0);
        carrier carr_12 = exp(b, fq_12, 0);

        signal geo_pi = sum(mix(X_01, carr_01), mix(X_12, carr_12));

        tx_channel dq = txch($q, “drive”);
        // play back to back geo pi pulses to get full state transfer
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
            for _ in [0:2] {
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

Shows how to do a qubit measurement within the signal framework.

.. code-block:: c

    // Use a boxcar function to generate IQ data from raw signal
    kernel boxcar(signal)->complex[64];
    // Use a linear discriminator to generate bits from IQ data
    kernel linear_disc(complex[64] iq)->bit;

    defcal measure $0 {
        // Define the channels
        txchannel m0 = txch($0, "measure");
        rxchannel cap0 = rxch($0, "capture");

        // Force time of carrier to 0 for consistent phase for discrimination.
        signal carr = set(exp(1.0, 5e9, 0), 0);

        // Apply measurement stimulus
        envelope meas_pulse = gaussian_square(1.0, 16000dt, 262dt, 13952dt);
        transmit(m0, mix(carrier, meas_pulse), meas_pulse.duration);

        // Align measure and capture channels
        barrier(m0, cap0);

        // Capture signal
        signal raw_output = receive(cap0, 16000dt);

        // Kernel and discriminate
        complex[32] iq = boxcar(raw_output);
        bit result = linear_disc(iq);

        return result;
    }

Rz gate (phase shift)
~~~~~~~~~~~~~~~~~~~~~

Shows how to do an Rz gate (e.g. phase shift) via signals.

.. code-block:: c

    defcal rz(angle[20] theta) $q {
        txchannel dq = txch($q, "drive");
        float[64] qub_freq = ...;
        carrier carr = exp(1.0, qub_freq, 0);
        signal sig = shift(carr, theta);
        transmit(dq, sig, 0);
    }

Qubit spectroscopy
~~~~~~~~~~~~~~~~~~

Construct a ``defcal`` for doing qubit spectroscopy. Gives the qubit resonant frequency value. This
example also demonstrates how ``defcal``'s can be used within a larger openqasm program.

.. code-block:: c

    // Computes index of largest entry in ``float[64]`` array
    kernel max_index(array[float[64], size] arr)->int[32];

    def spectro(int[32] shots, int[32] steps, float[64] freq_low, float[64] freq_high) qubit q -> float[64] {
        /** Compute qubit resonant frequency in a spectroscopy experiment.

        Args:
            shots: Number of shots to execute
            steps: Number of frequencies to use in the sweep.
            freq_low: Low end of frequency sweep.
            freq_high: High end of frequency sweep.

        Returns:
            Resonant frequencies of qubit q.
        **/
        array[float[64], steps] output;  // Array for output signal
        for s in [0:steps] {
            // Sweep freqs from ``freq_low`` to ``freq_high``
            float[64] curr_freq = freq_low + (freq_high-freq_low)*s/steps;
            // Compute the avg absolute value of the output iq signal over ``shots`` shots
            output[s] = 0;
            for i in [0:shots] {
                complex[64] iq = sp_cal(curr_freq) $q;
                float[64] abs_iq = abs(iq);  // Assue abs value for complex numbers
                output[s] = (output[s]*i + abs_iq)/(i+1);  // Update avg via recursive formula
            }
        }

        int[32] ind = max_index(output);
        // Resonance frequency
        float[64] res_freq = start + (end-start)*ind/points;

        return res_freq;
    }

    // Defcal for spectroscopy
    // NOTE: Assumed can pass other classical types to ``defcal``'s; need to consider this
    defcal sp_cal(float[64] freq) $q -> complex[64] {
        txchannel dq = txch($q, "drive");

        envelope env = gaussian(0.3, 1024dt, 256dt);
        carrier carr = exp(1.0, freq, 0.0);

        reset $q;  // Assume a valid reset calibration
        transmit(dq, mix(env, carr), env.duration);
        barrier_all();  // Sync all clocks
        complex[64] iq = measure $q;
        return iq;
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

Timing
------

Each ``channel`` maintains its own "clock". When a signal is transmitted/received, the channel clock
is played the clock for advances by the length of the signal (``signal.duration``).

``delay`` and ``barrier`` instructions in OpenPulse resolve timing as in the qubit case outlined in the
`Delays <delays.html>`_ section of this specification. At the pulse level, however, ``delay`` and ``barrier``
must take ``channels`` as input, rather than qubits.

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
between ``defcal``'s within a common program, however, so the first use of channels within a ``defcal``
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

``defcal`` blocks must have a well-defined length, which can be accessed via ``lengthof``.

Additional Considerations
-------------------------

- How do we handle ``defcal``'s that require classical input. For instance, spectroscopy as shown in
the document requires a frequency input. Similarly, in a Rabi experiment, an input amplitude will be
needed for the drive pulse. I added a suggestion for generic ``defcal``'s, which can take any
classical parameter. But there are other options as well.
    - Create an attribute system which allows tagging of certain properties to a ``defcal``. This is
along the lines of LLVM IR, for instance.
    - Allow global input from OpenQASM into ``defcal``'s.
    - Don't allow these advanced pulse experiments. The goal seems to be to move away from the pulse
model, abstracting everything into circuits. Perhaps we don't want to support this functionality going forward.
- Reuse of channels, carriers, etc... Since pulse syntax is local to ``defcal``'s, channels, carriers and signals have to be redefined within
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
    - Include a global ``backend`` property, from which channels can be retrieved. Something like
``backend.get_tx_channel($0, "drive")``. For carriers, if the backend is capable of returning the resonant
frequencies, that could be a good basis for prebuilt carriers likely to be reused.
