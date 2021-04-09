OpenPulse Grammar
=================

In addition to OpenQASM instructions, ``defcal`` blocks may contain OpenPulse
instructions. Certain OpenPulse instructions are further restricted to only
appearing inside of a ``defcal`` block.

These instructions are motivated by the original OpenPulse specification which
was defined as a JSON wire-format for pulse-level quantum programs in the paper
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment
<https://arxiv.org/abs/1809.03452>`_.
The text format described here has several advantages over the equivalent JSON
format:

- It is more readable
- Absolute time is handled through built-in timekeeping instructions
- Gates and classical instructions can be mixed in with the pulses to create far richer calibrations
- Pulse definitions are tied to circuit instructions rather than circuit programs
- Richer handling of frames

Channels
--------

Channels map to a hardware resource, which can play pulses to manipulate a qubit
or capture signal from the qubit to perform a measurement. There is a many-to-many
relationship between qubits and channels. One qubit may have multiple channels
connecting to it. Pulses on different channels would have different physical
interactions with that qubit. A channel may also have many qubits. For instance,
a channel could manipulate the coupling between two neighboring qubits, or
could even reference multiple qubits in a chain.

Channels are vendor-specific and device-specific. It is expected that vendors
of quantum hardware provide the appropriate channel names and qubit mappings
as configuration information to end users. Each channel may also have associated
static settings, such as local-oscillator frequencies, which do not vary
throughout program execution. Again it is expected that vendors of quantum
hardware provide a method for manipulating those static settings if appropriate.

There are two kinds of channels: transmit channels (sending input to a quantum
device) and receive channels (reading output from a quantum device).

Interacting with channels directly is onerous and makes the pulse programs less
portable. The OpenPulse defcalgrammar does not directly work with channels and
instead works with abstract "frames" of reference, described below. A channel
is only used to specify the physical resource on which to play a pulse.

Frames
------

When interacting with qubits, it turns out to be quite useful to keep track of a frame of reference,
akin to the rotating frame of a Hamiltonian, throughout the execution of a program. These frames
are responsible for two things

- Tracking time appropriately so programs do not need to deal in absolute time
- Tracking phase by producing a complex value given an input time (i.e. via the mathematical relationship
  :math:`e^{i\left(2\pi f t + \theta\right)}`,  where `f` is frequency and
  :math:`\theta` is phase).

The canonical motivation for keeping track of phase is to implement a "virtual
Z-gate", which does not require a physical pulse but rather shifts the phase of
all future pulses on that frame.

The ``frame`` type is a virtual resource and may be copied without a problem.
It is up to the compiler to choose how to implement the required transformations on
hardware The frame is composed of three parts:

1. A frequency ``frequency`` of type ``float``.
2. A phase ``phase`` of type ``angle``.
3. A time of type ``dt`` which is manipulated implicitly and cannot be modified other
   than through existing timing instructions like ``delay`` and ``barrier``.

It is initialized depending on how the frame is constructed (see below),
and the exact precision of these parameters is hardware specific.

Frame Construction
~~~~~~~~~~~~~~~~~~

Frames are purely virtual and can be constructed using the ``Frame`` command

.. code-block:: javascript

  driveframe = Frame(5e9, 0.0);

When instantiated, the frame time starts at 0. ``Frame``s can also be copied using the
``copy`` command with argument replacement

.. code-block:: javascript

  driveframe1 = Frame(1.0, 5e9, 0.0);
  driveframe2 = copy(driveframe1, phase=driveframe1.phase + pi/2);

This will generate a ::math:`pi/2` phase incremented copy of ``driveframe1`` (i.e. with
the same frequency and time as ``driveframe1``).

Like other things in OpenQASM, a ``frame`` is locally scoped and a prelude must be used to
instantiate frames in global scope.

Frame manipulation
~~~~~~~~~~~~~~~~~~

The (frequency, phase) tuple of a frame can be manipulated throughout program
by referencing ``.frequency``, and ``.phase``. Operations must be
appropriate for the respective type, ``float`` for frequency and ``angle`` for
phase. Again, the exact precision of these calculations is hardware specific.

Here's an example of manipulating the phase to calibrate an ``rz`` gate on a frame called
``driveframe``:

.. code-block:: javascript

   // Shift phase of the "drive" frame by pi/4, eg. an rz gate with angle -pi/4
   driveframe.phase += pi/4;

   // Define a calibration for the rz gate on all physical qubits
   defcal rz(angle[20]:theta) %q {
     driveframe.phase -= theta;
   }

Manipulating frames based on the state of other frames is also permitted:

.. code-block:: javascript

   // Swap phases between two frames
   const temp = frame1.phase;
   frame1.phase = frame2.phase;
   frame2.phase = temp;

Waveforms
---------

Waveforms are of type ``waveform`` and can either be:

- An array of complex samples which define the points for the waveform envelope
- An abstract mathematical function representing a waveform. This will later be
  materialized into a list of complex samples, either by the compiler or the hardware
  using the parameters provided to the pulse template.

A value of type ``waveform`` is retrieved by explicitly constructing the complex samples
or by calling one of the built-in waveform template functions. Note that each of these
functions takes a type ``length`` as a first argument, since pulses need to have a definite
length. Using the hardware dependent ``dt`` unit is recommended, since the compiler may need to
down-sample a higher precision waveform to physically realize it.

.. code-block:: javascript

   // arbitrary complex samples
   arb_waveform = [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j];

   // amp is waveform amplitude at center
   // center is the mean of waveform
   // sigma is the standard deviation of waveform
   gaussian(length:l, complex[float[32]]:amp, length:center, length:sigma)

   // amp is waveform amplitude at center
   // center is the mean of waveform
   // sigma is the standard deviation of waveform
   sech(length:l, complex[float[32]]:amp, length:center, length:sigma)

   // amp is waveform amplitude at center
   // center is the mean of waveform
   // square_width is the width of the square waveform component
   // sigma is the standard deviation of waveform
   gaussian_square(length:l, complex[float[32]]:amp, length:center, length:square_width, length:sigma)

   // amp is waveform amplitude at center
   // center is the mean of waveform
   // sigma is the standard deviation of waveform
   // beta is the Y correction amplitude, see the DRAG paper
   drag(length:l, complex[float[32]]:amp, length:center, length:sigma, float[32]:beta)

   // Define a constant waveform of length l
   constant(l:length)

   // Define a sine wave of a given amplitude, frequncy, phase, and length
   sine(l: length, complex[float[32]]:amp, float[32]: frequency, angle: phase)

We can manipulate the ``waveform`` types using the following signal processing functions to produce
new waveforms

- ``mix(wf1: waveform, wf2: waveform)`` -> waveform - Mix two input waveforms to produce a new waveform.
  This is equivalent to the product signal :math:`wf(t_i) = wf_1(t_i) \times wf_2(t_i)`
- ``sum(wf1: waveform, wf2: waveform)`` -> waveform - Sum two input waveforms to produce a new waveform.
- ``piecewise(wf0: waveform, wf1: waveform)`` -> waveform - Output waveform.
- ``offset(wf: waveform, amount: complex)`` -> waveform - Offset the input waveform by an amount.
- ``scale(wf: waveform, factor: complex)`` -> waveform - Scale the input waveform by a factor.
- ``conj(wf: waveform) -> waveform`` - Conjugate the input waveform.
- ``re(wf: waveform) -> waveform`` - Real component of input waveform.
- ``im(wf: waveform) -> waveform`` - Imaginary component of input waveform.
- ``abs(wf: waveform) -> waveform`` - Transform waveform as norm of input. waveform
- ``phase_shift(wf: waveform, ang: angle) -> waveform`` - Signal with relative phase, ang.

Play instruction
----------------

Waveforms are scheduled using the ``play`` instruction. These instructions may
only appear inside a ``defcal`` block!

Play instructions have two required parameters:

- a value of type ``waveform`` representing the waveform envelope
- the frame to use for the pulse
- the channel on which to play the pulse

.. code-block:: javascript

   // Play a 3 sample pulse on qubit 0's "drive" frame
   play(tx0, [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j], driveframe);

   // Play a gaussian on qubit 1's "drive" frame
   frame f1 = Frame(q1_freq, 0.0);
   play(tx0, gaussian(...), f1);

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

.. code-block:: javascript

   // Minimum requirement
   kernel capture(channel chan, frame output) -> complex[32];

   // A capture command with more features
   kernel capture(channel chan, frame output, pulse filter) -> complex[32];

The return type of a ``capture`` command varies. It could be a raw trace, ie. a
list of samples taken over a short period of time. It could be some averaged IQ
value. It could be a classified bit. Or it could even have no return value,
pushing the results into some buffer which is then accessed outside the program.

Timing
------

Each frame maintains its own "clock". When a pulse is played the clock for
that frame advances by the length of the pulse.

For frames, everything behaves analogous to qubits in the
`Delays <delays.html>`_ section of this specification. There are however some
small differences.

The ``delay`` instruction may take a frame instead of a qubit. The ``barrier``
instruction may also take a list of frames intead of a list of qubits.

``defcal`` blocks have an implicit barrier on every frame that enters the block,
meaning that those clocks are guaranteed to be aligned at the start of the block.
These blocks also need to have a well-defined length, similar to the ``boxas`` block.

.. code-block:: javascript

   waveform p = ...; // some 100dt waveform

   defcal simultaneous_pulsed_gate $0 {
     driveframe = Frame(1.0, 5e9, 0.0);
     play(tx0, p driveframe);
     delay[20dt] driveframe;
     // Starts the 100dt pulse 20dt into "drive0" already playing it
     play(tx0, p driveframe);
   }

Examples
--------

Cross-resonance gate
~~~~~~~~~~~~~~~~~~~~


.. code-block:: javascript

    // Initialize
    channel d0 = txch(0, "drive");
    channel d1 = txch(1, "drive");

    frame frame0 = Frame(5e9, 0);

    waveform wf1 = gaussian_square(1., 1024dt, 32dt, 128dt);
    waveform wf2 = gaussian_square(0.1, 1024dt, 32dt, 128dt);

    // phase update some virtual Z gate
    frame0.phase += pi/2;

    /*** Do pre-rotation ***/
    {...}

    // generate new frame for second drive -- frame can be discarded at will
    frame temp_frame = copy(frame0, phase=frame0.phase + pi/2);

    play(d0, wf1, frame0);
    play(d1, wf2, temp_frame);


    /*** Do post-rotation ***/
    {...}

Geometric gate
~~~~~~~~~~~~~~

.. code-block:: javascript

  defcal geo_gate(angle[32]: theta) $q {
      // theta: rotation angle (about z-axis) on Bloch sphere

      // Assume we have calibrated 0->1 pi pulses and 1->2 pi pulse
      // envelopes (no sideband)
      waveform X_01 = {...};
      waveform X_12 = {...};

      // Get 0->1 freq and anharmonicity for $q
      float[32] fq_01 = 5e9; // hardcode or pull from some function
      float[32] anharm = 300e6; // hardcode or pull from some function

      float[32] a = sin(theta/2);
      float[32] b = sqrt(1-a**2);
      // pi geo pulse envelope is: a*X_01 + b*X_12
      // X_01 has freq fq_01
      // X_12 has freq fq_01+anharm
      frame frame_01 = Frame(fq_01, 0);
      frame frame_12 = Frame(fq_12, 0);
      fence(.*);

      tx_channel dq = txch($q, “drive”);

      // Double-tap
      play(dq, scale(a, X_01), frame_01);
      play(dq, scale(b, X_12), frame_12);
      play(dq, scale(a, X_01), frame_01);
      play(dq, scale(b, X_12), frame_12);
  }

Neutral atoms
~~~~~~~~~~~~~

In this simple example, the signal chain is composed of two electro-optic modulators (EOM) and
an acousto-optic deflector (AOD). The EOMs put sidebands on the laser light while the AOD diffracts
the light in an amount proportional to the frequency of the RF drive. This example was chosen
because it is similar in spirit to the work by Levine et al. except that phase control is exerted
using virtual Z gates on the AODs -- requiring frame tracking of the qubit frequency yet
application of a tone that maps to the qubit position (i.e. requires the use of a sideband).

The program aims to perform a Hahn echo sequence on q1, and a Ramsey sequence on q2 and q3.

.. code-block:: javascript

  // Define the channels
  eom_a_channel = txch(0, "eom_a");
  eom_a_channel = txch(1, "eom_b");
  aod_channel = txch(0, "aod");

  // Define the Raman frames, which are detuned by an amount Δ from the  5S1/2 to 5P1/2 transition
  // and offset from each other by the qubit_freq
  raman_a_frame = Frame(Δ, 0.0)
  raman_b_frame = Frame(Δ-qubit_freq, 0.0)

  // Waveforms supplied to the Raman beams are just constant


  // Three copies of qubit freq to track phase of each qubit
  q1_frame = Frame(qubit_freq, 0)
  q2_frame = Frame(qubit_freq, 0)
  q3_frame = Frame(qubit_freq, 0)

  // Generic gaussian envelope
  waveform π_half_sig = gaussian(..., π_half_time, ...)

  // Waveforms ultimately supplied to the AODs. We mix our general Gaussian pulse with a sine wave to
  // put a sideband on the signal construction to target the qubit position while maintainig the
  // desired Rabi rate.
  q1_π_half_sig = mix(π_half_sig, sine(q1_π_half_amp, q1_pos_freq-qubit_freq, 0.0, π_half_time));
  q2_π_half_sig = mix(π_half_sig, sine(q2_π_half_amp, q2_pos_freq-qubit_freq, 0.0, π_half_time));
  q3_π_half_sig = mix(π_half_sig, sine(q3_π_half_amp, q3_pos_freq-qubit_freq, 0.0, π_half_time));

  for τ in [0: T]:
      // Simultaneous π/2 pulses
      play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
      play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
      play(aod_channel, q1_π_half_sig, q1_frame);
      play(aod_channel, q1_π_half_sig, q2_frame);
      play(aod_channel, q1_π_half_sig, q3_frame);

      // Time delay all
      delay(.*, τ/2)

      // π pulse on qubit 1 only -- composed of two π/2 pulses
      for _ in [0:1]:
          play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
          play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
          play(aod_channel, q1_π_half_sig, q1_frame);

      // Fence all then time delay
      fence(.*)
      delay(.*, τ/2)

      // Phase shift the signals by a different amount -- or should I be shifting qubit_#_signal?
      q1_frame.phase += tppi_1 * τ
      q1_frame.phase += tppi_2 * τ
      q1_frame.phase += tppi_3 * τ

      // Simultaneous π/2 pulses
      play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
      play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
      play(aod_channel, q1_π_half_sig, q1_frame);
      play(aod_channel, q1_π_half_sig, q2_frame);
      play(aod_channel, q1_π_half_sig, q3_frame);


Multiplexed readout and capture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we want to perform readout and capture of a pair of qubits, but mediated by a
single physical tx and rx channel. The example is for just two qubits, but works the same for
many (just adding more frames, waveforms, plays, and captures).

.. code-block:: javascript

  defcal multiplexed_readout_and_capture() $0 $1

    // the tx/rx channel is the same for $0 and $1
    tx_channel ro_tx = txch($0, "readout");
    rx_channel ro_rx = rxch($0, "readout");

    // readout frames of different frequencies
    q0_frame = Frame(q0_ro_freq, 0); // time 0
    q1_frame = Frame(q1_ro_freq, 0); // time 0

    // flat-top readout waveforms
    waveform q0_ro_wf = constant(amplitude=0.1, time=...);
    waveform q1_ro_wf = constant(amplitude=0.2, time=...);

    // multiplexed readout
    play(ro_tx, q0_ro_wf, q0_frame);
    play(ro_tx, q1_ro_wf, q1_frame);

    // simple boxcar kernel
    waveform ro_kernel = constant(amplitude=1, time=...);

    // multiplexed capture
    complex[32] q0_iqs = capture(ro_rx, q0_frame, ro_kernel);
    complex[32] q1_iqs = capture(ro_rx, q1_frame, ro_kernel);


Sample rate collisions
-----------------------

Incommensurate Rates
~~~~~~~~~~~~~~~~~~~~

Since the frame can be played on multiple channels, there may be an issue with sample rates. For example,

.. code-block:: javascript

  defcal incommensurate_rates_interval() $q
    tx0 = txch(0, "tx0"); # sample per 1 ns
    tx1 = txch(1, "tx1"); # sample per 2 ns

    waveform wf = gaussian_square(0.1, 13ns, ...);

    play(tx0, wf, driveframe);
    // now driveframe.time is at 13ns
    play(tx1, wf, driveframe); // does not support 13 ns -- either 12ns or 14 ns
  }

The implementation of this behavior is up to the vendor.

Incommensurate Lengths
~~~~~~~~~~~~~~~~~~~~~~

If the samples are defined dt, then playing the same waveform on two different channels
produces

.. code-block:: javascript

  defcal incommensurate_lengths() $q
    tx0 = txch(0, "tx0"); # sample per 1 ns
    tx1 = txch(1, "tx1"); # sample per 2 ns

    waveform wf = gaussian_square(0.1, 12dt, ...); // this means different lengths to different channels

    play(tx0, wf, driveframe);
    // now driveframe.time is at 12ns
    play(tx1, wf, driveframe);
    // now driveframe.time is at 36ns
  }

This is considered well-defined behavior.

Silly
-----

.. code-block:: javascript

   waveform p = ...; // some 100dt waveform

   // driveframe defined in prelude
   defcal simultaneous_pulsed_gate %0 {
     play(tx0, p, driveframe);
     fence(.*);

     frame new_frame = Frame(6.0, 0.0); // time is start of 0 or defcal
   }
