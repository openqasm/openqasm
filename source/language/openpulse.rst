OpenPulse Grammar
=================

*The OpenPulse grammar is still in active development and is liable to change.*

OpenQASM allows users to provide the target system's implementation of quantum operations
with ``defcal`` blocks . Calibration grammars are open to extension for system implementors. In
this document, we outline one such grammar, OpenPulse, which may be selected within a supporting
compiler through the declaration ``defcalgrammar "openpulse";``.

This grammar is primarily motivated by the original OpenPulse specification, a JSON wire-format for
pulse-level quantum programs defined in the paper `Qiskit Backend Specifications for OpenQASM
and OpenPulse Experiment`_:cite:`mckay2018`, however, is also inspired directly or indirectly through
other `efforts in the field`_:cite:`alexanderQiskitPulseProgramming2020a,DiCarloLabDelftPycQEDPy32021,ExperimentalMicroarchitectureSuperconducting,nguyenEnablingPulselevelProgramming2020,QuillangQuil2021`.

The textual format described here has several advantages over the original JSON format:

- Improved readability.
- Pulse timing is based on instruction ordering and works with programs containing branching
  control flow.
- Reusable gate calibrations enable more succinct calibration descriptions.
- Pulse definitions are declared as a calibration for individual circuit instructions attached to
  physical qubits enabling the microcoding of gate level operations.
- Richer ability to compose complex pulses through natural DSP-like operations.
- Clearly defined relationship between pulses, channels and the phases of compilation to
  hardware resources.
- Use of multiple frames on a single channel at the same time (see :ref:`Geometric gate`).


Openpulse provides a flexible programming model that should extend to many quantum control schemes
and hardware. At the core of the OpenPulse grammar are the concepts of ``frames``, ``waveforms`` and ``channels``.
``frames`` are used to schedule the playing of a ``waveform`` or capturing of data
via a ``channel`` on the target device. A ``channel`` is a software abstraction which allows the
programmer to be agnostic to complexities of the device's underlying pulse generation hardware. It
is the responsibility of the target device's compiler to map ``frames`` to the applied ``channel``s in
target hardware.


Channels
--------

Channels map to hardware resources, which can play pulses stimuli or capture data. In practice,
channels are used to manipulate and observe qubits. There is a many-to-many
relationship between qubits and channels. One qubit may have multiple channels
connecting to it. Pulses on different channels would have different physical
interactions with that qubit and thereby control different operations. A channel may also have many qubits. For instance,
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

A channel is only used to specify the physical resource on which to play a pulse or from which
to capture data. This specification should be done by providing a mapping between a qubit list +
name and the configured hardware channel. The hardware can then be accessed as
OpenPulse ``channel``'s via the "getchannel" function which allows identifying a channel by a variadic combination
of string name and qubits.

.. code-block:: c

    getchannel(str name, qubit q0, ..., qubit qn) -> channel  // get a channel

The qubits must be **physical** qubits. Furthermore, ordering of qubits is important. For instance,
``getchannel("control", $0, $1)`` and ``getchannel("control", $1, $0)`` may be used to implement distinct
cross-resonance gates. It is also possible to access a channel by its full name, without supplying
any qubits, if that has been implemented by the vendor. For instance, ``getchannel("<channel_name>")``
may refer to a transmit channel with an arbitrary name.

.. code-block:: c

    channel d0 = getchannel("drive", $0);  // channel for driving at qubit $0's freq
    channel cr1_2 = getchannel("coupler", $1, $2);  // channel for a coupler between two qubits
    channel m2 = getchannel("measure", $2);  // channel for transmitting measurement stimulus

    channel global_field = getchannel("global_field"); // channel not associated with any qubits

    // capture channels for capturing qubits $0 and $1
    channel cap0 = getchannel("capture", $0);
    channel cap1 = getchannel("capture", $1);

Frames
------

When interacting with qubits, it is necessary to keep track of a frame of reference, akin to the rotating
frame of a Hamiltonian, throughout the execution of a program. Openpulse provides the ``frame``
type which is responsible for tracking two properties:

- Tracking time appropriately so programs do not need to deal in absolute time or with the
  bookkeeping of advancing time in a sequence of pulses.
- Tracking phase by producing a complex value given an input time (i.e. via the mathematical
  relationship :math:`e^{i\left(2\pi f t + \theta\right)}`,  where `f` is frequency and
  :math:`\theta` is phase). One motivation for keeping track of phase is to allow pulses to be
  defined in the rotating frame with the effect being an equivalent application in the lab
  frame (i.e. with the carrier supplied by the ``frame``). Another motivation is to more naturally
  implement a "virtual Z-gate", which does not require a physical pulse but rather shifts the phase
  of all future pulses on that frame.

The frame is composed of three parts:

1. A frequency ``frequency`` of type ``float``.
2. A phase ``phase`` of type ``angle``.
3. A time which is manipulated implicitly and cannot be modified other
   than through existing timing instructions like ``delay`` and ``barrier``. The time increment
   is determined by the channel on which the frame is played (see :ref:`Timing` section).

The ``frame`` type is a virtual resource and the exact precision of these parameters is
hardware specific. It is thus up to the compiler to choose how to implement the required
transformations to physical resources in hardware (e.g. mapping multiple frames to a
single `numerically-controlled oscillator (NCO) <https://en.wikipedia.org/wiki/Numerically-controlled_oscillator>`_).

Frame Construction
~~~~~~~~~~~~~~~~~~

Frames can be constructed using the ``newframe`` command e.g.

.. code-block:: javascript

  frame driveframe = newframe(5e9, 0.0); // newframe(float[size] frequency, angle[size] phase)

would construct a frame with a frequency of 5 GHz and a phase of 0.0. When
instantiated, the frame time starts at 0. ``frame``\s can also be copied using the
``copyframe`` command

.. code-block:: javascript

  frame driveframe1 = newframe(5e9, 0.0);
  frame driveframe2 = copyframe(driveframe1);
  driveframe2.phase = driveframe1.phase + pi/2;

This will generate a :math:`\pi/2` phase incremented copy of ``driveframe1`` with the same
frame manipulation
~~~~~~~~~~~~~~~~~~

The (frequency, phase) tuple of a frame can be manipulated throughout program
by referencing ``.frequency``, and ``.phase``. Operations must be
appropriate for the respective type, ``float`` for frequency and ``angle`` for
phase. Again, the exact precision of these calculations is hardware specific.

Here's an example of manipulating the phase to calibrate an ``rz`` gate on a frame called
``driveframe``:

.. code-block:: javascript

   // Example 1: Shift phase of the "drive" frame by pi/4, to realize a virtual rz gate with angle -pi/4
   cal {
     driveframe.phase += pi/4;
   }

   // The following is an example only. Frames as arrays has not been agreed on.
   // This conceptually must be compile-time arrays and treat qubits as indices
   // which also has not been well-defined. We are exploring other solutions to
   // the problem of mapping qubits to pulse-level resources.

   // Example 2: Define a calibration for the rz gate on all 8 physical qubits
   cal {
     array[frame, 8] rz_frames;
     frame[0] = newframe(...);
     // and so on
   }

   defcal rz(angle[20] theta) $q {
     rz_frames[q].phase -= theta;
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
or by calling one of the built-in waveform template functions. The latter are initialized by
assigning a ``waveform`` to the result of a function call. Note that each of these
extern functions takes a type ``length`` as a first argument, since waveforms need to have a
definite length. Using the hardware dependent ``dt`` unit is recommended for this length,
since the compiler may need to down-sample a higher precision waveform to physically realize it.

.. code-block:: javascript

   // arbitrary complex samples
   waveform arb_waveform = [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j];

   // amp is waveform amplitude at center
   // l is the overall length of the waveform
   // sigma is the standard deviation of waveform
   gaussian(complex[size] amp, length l, length sigma) -> waveform;

   // amp is waveform amplitude at center
   // l is the overall length of the waveform
   // sigma is the standard deviation of waveform
   sech(complex[size] amp, length l, length sigma) -> waveform;

   // amp is waveform amplitude at center
   // l is the overall length of the waveform
   // square_width is the width of the square waveform component
   // sigma is the standard deviation of waveform
   gaussian_square(complex[size] amp, length l, length square_width, length sigma) -> waveform;

   // amp is waveform amplitude at center
   // l is the overall length of the waveform
   // sigma is the standard deviation of waveform
   // beta is the Y correction amplitude, see the DRAG paper
   drag(complex[size] amp, length l, length sigma, float[size] beta) -> waveform;

   // amp is waveform amplitude
   // l is the overall length of the waveform
   constant(complex[size] amp, length l) -> waveform;

   // amp is waveform amplitude
   // l is the overall length of the waveform
   // frequency is the frequency of the waveform
   // phase is the phase of the waveform
   sine(complex[size] amp, length  l, float[size] frequency, angle[size] phase) -> waveform;

We can manipulate the ``waveform`` types using the following signal processing functions to produce
new waveforms (this list may be updated as more functionality is required).

.. code-block:: javascript

    // Multiply two input waveforms entry by entry to produce a new waveform
    // :math:`wf(t_i) = wf_1(t_i) \times wf_2(t_i)`
    mix(waveform wf1, waveform wf2) -> waveform;

    // Sum two input waveforms entry by entry to produce a new waveform
    // :math:`wf(t_i) = wf_1(t_i) + wf_2(t_i)`
    sum(waveform wf1, waveform wf2) -> waveform;

    // Add a relative phase to a waveform (ie multiply by :math:`e^{\imag \theta}`)
    phase_shift(waveform wf, angle ang) -> waveform;

    // Scale the amplitude of a waveform's samples producing a new waveform
    scale(waveform wf, float factor) -> waveform;

Play instruction
----------------

Waveforms are scheduled using the ``play`` instruction. These instructions may
only appear inside a ``defcal`` block and have three required parameters:

- The channel on which to play the pulse.
- A value of type ``waveform`` representing the waveform envelope.
- The frame to use for the pulse.

.. code-block:: javascript

  play(channel chan, waveform wfm, frame fr)

For example,

.. code-block:: javascript

  defcal play_my_pulses {
   // Play a 3 sample pulse on the tx0 channel
   play(tx0, [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j], driveframe);

   // Play a gaussian pulse on the tx1 channel
   frame f1 = newframe(q1_freq, 0.0);
   play(tx1, gaussian(...), f1);
  }

Capture Instruction
-------------------

Acquisition is scheduled by a ``capture`` instruction. This is a special
``extern`` function which is specified by a hardware vendor. The measurement
process is difficult to describe generically due to the wide variety of
hardware and measurement methods. Like the play instruction, these instructions
may only appear inside a ``defcal`` or ``cal`` block.

The only required parameters are the ``channel`` and the ``frame``.

The following are possible parameters that might be included:

- A "duration" of type ``length``, if it cannot be inferred from other parameters.
- A "filter" of type ``waveform``, which is dot product-ed with the measured IQ to distill the
  result into a single IQ value

Again it is up to the hardware vendor to determine the parameters and write a
extern definition at the top-level, such as:

.. code-block:: javascript

   // Minimum requirement
   extern capture(channel chan, frame output);

   // A capture command that returns an iq value
   extern capture(channel chan, waveform filter, frame output) -> complex[32];

   // A capture command that returns a discrimnated bit
   extern capture(channel chan, waveform filter, frame output) -> bit;

   // A capture command that returns a raw waveform data
   extern capture(channel chan, length len, frame output) -> waveform;

  // A capture that returns a count e.g. number of photons detected
  kernel capture(channel chan, length len, frame output) -> int

The return type of a ``capture`` command varies. It could be a raw trace, ie., a
list of samples taken over a short period of time. It could be some averaged IQ
value. It could be a classified bit. Or it could even have no return value,
pushing the results into some buffer which is then accessed outside the program.

For example, the ``capture`` instruction could return raw waveform data that is then
discriminated using user-defined boxcar and discrimination ``extern``s.

.. code-block:: javascript

    // Use a boxcar function to generate IQ data from raw waveform
    extern boxcar(waveform input) -> complex[64];
    // Use a linear discriminator to generate bits from IQ data
    extern discriminate(complex[64] iq) -> bit;

    defcal measure $0 -> bit {
        // Define the channels
        channel m0 = getchannel("measure", $0);
        channel cap0 = getchannel("capture", $0);

        // Force time of carrier to 0 for consistent phase for discrimination.
        frame stimulus_frame = newframe(5e9, 0);
        frame capture_frame = newframe(5e9, 0);

        // Apply measurement stimulus
        waveform meas_wf = gaussian_square(1.0, 16000dt, 262dt, 13952dt);

        // Play the stimulus
        play(m0, meas_wf, stimulus_frame);
        // Align measure and capture channels
        barrier(stimulus_frame, capture_frame);
        // Capture transmitted data after interaction with measurement resonator
        // extern capture(channel chan, length duration, frame capture_frame) -> waveform;
        waveform raw_output = capture(cap0, 16000dt, capture_frame);

        // Kernel and discriminate
        complex[32] iq = boxcar(raw_output);
        bit result = discriminate(iq);

        return result;
    }


Timing
------

Each frame maintains its own "clock". When a pulse is played the clock for
that frame advances by the length of the pulse.

For frames, everything behaves analogous to qubits in the
`Delays <delays.html>`_ section of this specification. There are however some
small differences.

The ``delay`` instruction may take a frame instead of a qubit. The ``barrier``
instruction may also take a list of frames instead of a list of qubits and aligns the time
of the clocks given as arguments.

``defcal`` blocks have an implicit ``barrier`` on every frame that enters the block,
meaning that those clocks are guaranteed to be aligned at the start of the block.
These blocks also need to have a well-defined length calculable at compile-time
to enable scheduling at the circuit level.

.. code-block:: javascript

   cal {
     waveform p = ...; // some 100dt waveform
     frame driveframe1 = newframe(5.0e9, 0);
     frame driveframe2 = newframe(6.0e9, 0);
   }

   defcal aligned_gates $0, $1 {
     // driveframe1 and driveframe2 used in this defcal, so clocks are aligned
     play(tx0, p, driveframe1);
     delay[20dt] driveframe1;
     // Clocks now unaligned by 120dt, so we use a `barrier` to re-align
     barrier(driveframe1, driveframe2);
     // `driveframe2` will now play a pulse 20dt after `driveframe1` finishes playing
     play(tx0, p, driveframe2);
   }

Examples
--------

Rabi Spectroscopy
~~~~~~~~~~~~~~~~~

Rabi spectroscopy experiments consist of a pulse that drives the qubit transition followed by a
measurement. Exploring the response to sweeps of pulse frequency, time, amplitude, or even
multi-dimensional sweeps reveals spectroscopic information about the qubit transition frequencies
and the drive strength. We describe these circuits with a mixture of conventional OpenQASM for the
simple pulse and measure sequence and step into `cal` blocks to access pulse level control. We
assume that the OpenQASM text is generated by some higher level language bindings and we only write
into the program the sweep where we can take advantage of the execution speed of sweeping as part of
the program.

**Qubit Spectroscopy**

Here we want to sweep the frequency of a long pulse that saturates the qubit transition.

.. code-block:: javascript

  // sweep parameters would be programmed in by some higher level bindings
  const float frequency_start = 4.5e9;
  const float frequency_step = 1e6
  const int frequency_num_steps = 301;

  // define a long saturation pulse of a set length and amplitude
  defcal saturation_pulse $0 {
      // assume channel and frame can be linked from a vendor supplied `cal` block
      play(tx0, constant(0.1, 100e-6), driveframe);
  }

  // step into a `cal` block to set the start of the frequency sweep
  cal {
      driveframe.frequency = frequency_start;
  }

  for i in [1:frequency_num_steps] {
      // step into a `cal` block to adjust the pulse frequency via the frame frequency
      cal {
          driveframe.frequency += frequency_step;
      }

      saturation_pulse $0;
      measure $0;
  }

**Rabi Time Spectroscopy**

Here we want to sweep the time of the pulse and observe coherent Rabi flopping dynamics.

.. code-block:: javascript

  const duration pulse_length_start = 20dt;
  const duration pulse_length_step = 1dt;
  const int pulse_length_num_steps = 100;

  for i in [1:pulse_length_num_steps] {
      duration pulse_length = pulse_length_start + (i-1)*pulse_length_step);
      duration sigma = pulse_length / 4;
      // since we are manipulating pulse lengths it is easier to define and play the waveform in a `cal` block
      cal {
          waveform wf = gaussian(0.5, pulse_length, sigma);
          // assume channel and frame can be linked from a vendor supplied `cal` block
          play(tx0, wf, driveframe);
      }
      measure 0;
  }

Cross-resonance gate
~~~~~~~~~~~~~~~~~~~~


.. code-block:: javascript

  cal {
     frame frame0 = newframe(5.0e9, 0);
  }

  defcal cross_resonance $0, $1 {
      // Access globally (or externally) defined channels
      channel d0 = getchannel("drive", $0);
      channel d1 = getchannel("drive", $1);

      waveform wf1 = gaussian_square(1., 1024dt, 128dt, 32dt);
      waveform wf2 = gaussian_square(0.1, 1024dt, 128dt, 32dt);

      /*** Do pre-rotation ***/

      // generate new frame for second drive that is locally scoped
      frame temp_frame = copyframe(frame0);

      // Pulses below occur simultaneously
      barrier(frame0, temp_frame);
      play(d0, wf1, frame0);
      play(d1, wf2, temp_frame);

      /*** Do post-rotation ***/

  }

Geometric gate
~~~~~~~~~~~~~~

.. code-block:: javascript

  cal {
      float fq_01 = 5e9; // hardcode or pull from some function
      float anharm = 300e6; // hardcode or pull from some function
      frame frame_01 = newframe(fq_01, 0);
      frame frame_12 = newframe(fq_01 + anharm, 0);
  }

  defcal geo_gate(angle[32] theta) $q {
      // theta: rotation angle (about z-axis) on Bloch sphere

      // Access globally defined channels
      channel dq = getchannel("drive", $q);

      // Assume we have calibrated 0->1 pi pulses and 1->2 pi pulse
      // envelopes (no sideband)
      waveform X_01 = {...};
      waveform X_12 = {...};
      float[32] a = sin(theta/2);
      float[32] b = sqrt(1-a**2);

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
because it is similar in spirit to the work by Levine et al._:cite:`levine2019` except that phase
control is exerted using virtual Z gates on the AODs -- requiring frame tracking of the qubit
frequency yet application of a tone that maps to the qubit position (i.e. requires the use of a
sideband).

The program aims to perform a Hahn echo sequence on q1, and a Ramsey sequence on q2 and q3.

.. code-block:: javascript

  // TODO: This example is incomplete, missing constant definitions and calling workflow.

  defcal neutral_atoms {
    // Access globally defined channels
    channel eom_a_channel = getchannel("eom_a", 0);
    channel eom_a_channel = getchannel("eom_b", 1);
    channel aod_channel = getchannel("aod", 0);

    // Define the Raman frames, which are detuned by an amount Δ from the  5S1/2 to 5P1/2 transition
    // and offset from each other by the qubit_freq
    frame raman_a_frame = newframe(Δ, 0.0)
    frame raman_b_frame = newframe(Δ-qubit_freq, 0.0)

    // Three copies of qubit freq to track phase of each qubit
    frame q1_frame = newframe(qubit_freq, 0)
    frame q2_frame = newframe(qubit_freq, 0)
    frame q3_frame = newframe(qubit_freq, 0)

    // Generic gaussian envelope
    waveform π_half_sig = gaussian(..., π_half_time, ...)

    // Waveforms ultimately supplied to the AODs. We mix our general Gaussian pulse with a sine wave to
    // put a sideband on the signal construction to target the qubit position while maintainig the
    // desired Rabi rate.
    waveform q1_π_half_sig = mix(π_half_sig, sine(q1_π_half_amp, π_half_time, q1_pos_freq-qubit_freq, 0.0));
    waveform q2_π_half_sig = mix(π_half_sig, sine(q2_π_half_amp, π_half_time, q2_pos_freq-qubit_freq, 0.0));
    waveform q3_π_half_sig = mix(π_half_sig, sine(q3_π_half_amp, π_half_time, q3_pos_freq-qubit_freq, 0.0));

    for τ in [0: T]:
        // Simultaneous π/2 pulses
        play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
        play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
        play(aod_channel, q1_π_half_sig, q1_frame);
        play(aod_channel, q1_π_half_sig, q2_frame);
        play(aod_channel, q1_π_half_sig, q3_frame);

        // Time delay all
        delay(τ/2);

        // π pulse on qubit 1 only -- composed of two π/2 pulses
        for _ in [0:1]:
            play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
            play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
            play(aod_channel, q1_π_half_sig, q1_frame);

        // Barrier all then time delay all
        barrier();
        delay(τ/2);

        // Phase shift the signals by a different amount
        q1_frame.phase += tppi_1 * τ;
        q2_frame.phase += tppi_2 * τ;
        q3_frame.phase += tppi_3 * τ;

        // Simultaneous π/2 pulses
        play(eom_a_channel, constant(raman_a_amp, π_half_time) , raman_a_frame);
        play(eom_b_channel, constant(raman_b_amp, π_half_time) , raman_b_frame);
        play(aod_channel, q1_π_half_sig, q1_frame);
        play(aod_channel, q1_π_half_sig, q2_frame);
        play(aod_channel, q1_π_half_sig, q3_frame);
  }

Multiplexed readout and capture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we want to perform readout and capture of a pair of qubits, but mediated by a
single physical transmission and capture channel. The example is for just two qubits, but works the same for
many (just adding more frames, waveforms, plays, and captures).

.. code-block:: javascript

  defcal multiplexed_readout_and_capture $0, $1 {

      // the transmission/captures channels are the same for $0 and $1
      channel ro_tx = getchannel("readout_tx", $0);
      channel ro_rx = getchannel("readout_rx", $0);

      // readout frames of different frequencies
      frame q0_frame = newframe(q0_ro_freq, 0); // time 0
      frame q1_frame = newframe(q1_ro_freq, 0); // time 0

      // flat-top readout waveforms
      waveform q0_ro_wf = constant(amp=0.1, l=...);
      waveform q1_ro_wf = constant(amp=0.2, l=...);

      // multiplexed readout
      play(ro_tx, q0_ro_wf, q0_frame);
      play(ro_tx, q1_ro_wf, q1_frame);

      // simple boxcar kernel
      waveform ro_kernel = constant(amp=1, l=...);

      // multiplexed capture
      // extern capture(channel chan, waveform ro_kernel, frame capture_frame) -> bit;
      bit q0_bit = capture(ro_rx, ro_kernel, q0_frame);
      bit q1_bit = capture(ro_rx, ro_kernel, q1_frame);
      ...
  }


Sample rate collisions
-----------------------

Incommensurate Rates
~~~~~~~~~~~~~~~~~~~~

Since the frame can be played on multiple channels, there may be an issue with sample rates.
For example,

.. code-block:: javascript

  defcal incommensurate_rates_interval $q
    channel tx0 = getchannel("tx0", 0); # sample per 1 ns
    channel tx1 = getchannel("tx1", 1); # sample per 2 ns

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

  defcal incommensurate_lengths $q
    channel tx0 = getchannel("tx0", 0); # sample per 1 ns
    channel tx1 = getchannel("tx1", 1); # sample per 2 ns

    waveform wf = gaussian_square(0.1, 12dt, ...); // this means different lengths to different channels

    play(tx0, wf, driveframe);
    // now driveframe.time is at 12ns
    play(tx1, wf, driveframe);
    // now driveframe.time is at 36ns
  }

This is considered well-defined behavior.

Open Questions
~~~~~~~~~~~~~~

- How do we handle mapping wildcarded qubits to arbitrary pulse-level resources?
- Do we define scheduling primitives for aligning pulses within defcals?
- How do we express general calibration experiments within defcals and call them within an openqasm program.
- How do we differentiate channel resource types?
- Is timing on frames, and channels as resources clear?
- How will hardware attributes be handled?
