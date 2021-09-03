OpenPulse Grammar
=================

*The OpenPulse grammar is still in active development and is liable to change. If you are working on an implementation and find this specification unclear or not supporting your use-cases, please join our community effort to improve pulse-level support in OpenQasm.*

OpenQASM allows users to provide the target system's implementation of quantum operations
with ``cal`` and ``defcal`` blocks . Calibration grammars are open to extension for system implementors. In
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

Openpulse provides a flexible programming model that should extend to many quantum control schemes
and hardware. At the core of the OpenPulse grammar are the concepts of ``port``s, ``waveform``s and, ``frame``s.
A ``port`` is a software abstraction representing any input or output component controlling qubits. It allows
a hardware vendor to provide relevant actuation knobs they wish to expose to the user in order to manipulate and observe
qubits, while hiding the complexities of the device's underlying hardware. A ``waveform`` is a time-dependent envelope
that can be used to emit signals on an output port or receive signals from an input port. A ``frame`` is also a software
abstraction that acts as both a (1) *clock* within the quantum program with its time being incremented on each usage and
(2) a stateful `carrier signal <https://en.wikipedia.org/wiki/Carrier_wave>`_ defined by a frequency and phase. As such,
when transmitting signals to the qubit, a ``frame`` determines time at which the ``waveform`` envelope is emitted, its
carrier frequency, and it's phase offset (see :ref:`Play`  section for more details). When capturing signals from a qubit,
at minimum a ``frame`` determines the time at which the signal is captured (see :ref:`Capture` section
for more details).

Note that this proposal fully supports and specifies scheduling when resources map to the qubits specified within
the defcal. However, it is possible for pulse-level resources to manipulate qubits that are not specified in the
``defcal``'s signature. As a future extension the language may support conveying to the scheduling layer which
resources are acted upon by a ``defcal``  such that the scheduler may faithfully schedule the target program to
hardware resources.


Ports
--------

A port is a software abstraction representing any input or output component meant to manipulate and observe qubits. Ports
are ultimately mapped to some combination of hardware resources, and there are varying versions of
this mapping with differing granularity. For instance, a port may directly map to a digital-to-analog converter.
Alternatively, a port may map to a combination of a digital NCO, analog-to-digital coverter, local oscillator, and amplifier.
A single port may even map to multiple transmit (or receive) hardware that must work in synchronicity.
Ultimately, it is simply a means by which a hardware vendor can provide relevant actuation knobs they wish to expose to the user
in order to manipulate and observe qubits. As such, the level of granularity of the mapping is up to the hardware vendor.

There is a many-to-many relationship between qubits and ports. One qubit may have multiple ports
connecting to it. Pulses on different ports would have different physical
interactions with that qubit and thereby control different operations. A port may also have many qubits. For instance,
a port could manipulate the coupling between two neighboring qubits, or
could even reference multiple qubits in a chain.

Ports are vendor-specific and device-specific. It is expected that vendors
of quantum hardware provide the appropriate port names and qubit mappings
as configuration information to end users. Each port may also have associated
static settings, such as local-oscillator frequencies, which do not vary
throughout program execution. Again it is expected that vendors of quantum
hardware provide a method for manipulating those static settings if appropriate.

There are two kinds of ports: transmit ports (sending input to a quantum
device) and receive ports (reading output from a quantum device).

A port is only used to specify the physical resource on which to play a pulse or from which
to capture data. The hardware can be accessed as OpenPulse ``port``'s via ``extern``
identifier that specifies an external linkage that will be resolved at compile-time via vendor
supplied translation units.

.. code-block:: c

    extern port drive_port0


It is expected that a hardware vendor provide some documentation as to the associated
functionality of a port (e.g. `drive_port0` referse to the XY control line of a qubit 0).

Frames
------

When interacting with qubits, it is necessary to keep track of a frame of reference, akin to the rotating
frame of a Hamiltonian, throughout the execution of a program. Openpulse provides a software abstraction of
``frame`` type which is responsible for tracking two properties:

- Tracking time appropriately so programs do not need to deal in absolute time or with the
  bookkeeping of advancing time in a sequence of pulses.
- Tracking accrued phase by producing a complex value given an input time (i.e. via the mathematical
  relationship :math:`e^{i\left(2\pi f t + \theta\right)}`,  where `f` is frequency and
  :math:`\theta` is the accrued phase). In this way,  a ``frame`` type behaves analogously to
  a `numerically-controlled oscillator (NCO) <https://en.wikipedia.org/wiki/Numerically-controlled_oscillator>`_).
  One motivation for keeping track of accured phase is to allow pulses to be defined in the rotating frame with the
  effect being an equivalent application in the lab frame (i.e. with the carrier supplied by the ``frame``).
  Another motivation is to more naturally implement a "virtual Z-gate", which does not require a physical pulse but
  rather shifts the phase of all future pulses on that frame.

The frame is composed of four parts:

1. A ``port`` to which it is attached. This can only be set upon initialization, and never changed subsequently.
2. A frequency ``frequency`` of type ``float``.
3. A phase ``phase`` of type ``angle``.
4. A time of type ``duration`` which is manipulated implicitly and cannot be modified other
   than through the existing timing instructions of ``delay``, ``play``, ``capture``,  and ``barrier``.
   The time increment is determined by the port on which the frame is played (see :ref:`Timing` section).

A ``frame`` from an existing calibration can also be accessed via an ``extern`` identifier

.. code-block:: c

    extern frame xy_frame0

Note that a ``frame`` type is a virtual resource and it is up to the hardware vendor's backend compiler
to choose how to implement the required transformations to physical resources in hardware during the machine code
generation phase.

Frame Initialization
~~~~~~~~~~~~~~~~~~

Frames can be initialized using the ``newframe`` command by providing the ``port``, ``frequency``, and ``phase`` e.g.

.. code-block:: javascript

  extern port drive0;
  frame driveframe0 = newframe(drive0, 5e9, 0.0); // newframe(port pr, float[size] frequency, angle[size] phase)

would initialize a frame on the ``drive0`` port with a frequency of 5 GHz, and phase of 0.0. Importantly,
a frame can be initializated in either a ``cal`` or ``defcal`` block which means that the time with which it is
initialized is the start time of the containing block (see :ref:`Timing` section for more details).

If a compiler toolchain is unable to support the initialization of ``frame``s within ``defcal``s, it is expected
to raise a compile-time error when such an initialization is encountered.

Note that multiple frames may address the same port e.g.

.. code-block:: javascript

  extern port measure_port;
  frame measure_frame_0 = newframe(measure_port, 5e9, 0.0);
  frame measure_frame_1 = newframe(measure_port, 5e9, 0.0);
  frame measure_frame_2 = newframe(measure_port, 5e9, 0.0);
  frame measure_frame_3 = newframe(measure_port, 5e9, 0.0);

The limitation on the number of frames that may address the same port depends entirely on hardware vendor
and how they choose to map ``frame``s to physical resources during the backend machine code generation phase.
For example, a hardware vendor may choose to collapse all ``frame``s attached to the same port into to a single
NCO in analogy to virtual to physical register allocation.


Frame Manipulation
~~~~~~~~~~~~~~~~~~

The (frequency, phase) tuple of a frame can be manipulated throughout program
by referencing ``.frequency``, and ``.phase``, with updates applied immediately
at the current time of the frame. Operations must be appropriate for the respective type,
``float`` for frequency and ``angle`` for phase. Again, the exact precision of these calculations
is hardware specific. If either the frequency or phase are set to values that are invalid for
the hardware, the compiler shall raise a compile-time error.

Here's an example of manipulating the phase to calibrate an ``rz`` gate on a frame called
``driveframe``:

.. code-block:: javascript

  ...

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
   const angle temp = frame1.phase;
   frame1.phase = frame2.phase;
   frame2.phase = temp;

Changing the frequency or phase is an instantaneous operation. If a vendor
is unable to support such instantaneous operations, it is expected that the
compiler shall raise a compile-time error when encountering such frame manipulations.

Waveforms
---------

Waveforms are of type ``waveform`` and can either be:

- An array of complex samples which define the points for the waveform envelope
- An abstract mathematical function representing a waveform. This will later be
  materialized into a list of complex samples, either by the compiler or the hardware
  using the parameters provided to the ``extern`` defined pulse template.

A value of type ``waveform`` may be defined either by explicitly constructing the complex samples
or by calling one of the waveform template functions provided by the target device.
Note that each of these extern functions takes a type ``duration`` as an argument,
since waveforms must have a definite duration.
Using the hardware dependent ``dt`` unit is recommended for this duration,
since otherwise the compiler may need to down-sample a higher precision
waveform to physically realize it.

Like other extern functions, ``extern waveform`` functions will be compiled.
But for static waveforms, the optimizing compiler should decide to execute this
at compile time and load the waveform into memory once.
For dynamic waveforms, the compiler just compiles and links this, to be executed at runtime.
We provide the ``waveform`` type in addition to the complex list of samples to
provide more context to compilers and hardware. For example, some hardware pulse
generators may have optimized implementations of common pulse shapes like gaussians.
Providing structured gaussian parameters instead of the materialized list of complex
samples provides optimization opportunities that wouldn't be available otherwise.

.. code-block:: javascript

   // arbitrary complex samples
   waveform arb_waveform = [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j];

   // amp is waveform amplitude at center
   // d is the overall duration of the waveform
   // sigma is the standard deviation of waveform
   extern gaussian(complex[float[size]] amp, duration d, duration sigma) -> waveform;

   // amp is waveform amplitude at center
   // d is the overall duration of the waveform
   // sigma is the standard deviation of waveform
   extern sech(complex[float[size]] amp, duration d, duration sigma) -> waveform;

   // amp is waveform amplitude at center
   // d is the overall duration of the waveform
   // square_width is the width of the square waveform component
   // sigma is the standard deviation of waveform
   extern gaussian_square(complex[float[size]] amp, duration d, duration square_width, duration sigma) -> waveform;

   // amp is waveform amplitude at center
   // d is the overall duration of the waveform
   // sigma is the standard deviation of waveform
   // beta is the Y correction amplitude, see the DRAG paper
   extern drag(complex[float[size]] amp, duration d, duration sigma, float[size] beta) -> waveform;

   // amp is waveform amplitude
   // d is the overall duration of the waveform
   extern constant(complex[float[size]] amp, duration d) -> waveform;

   // amp is waveform amplitude
   // d is the overall duration of the waveform
   // frequency is the frequency of the waveform
   // phase is the phase of the waveform
   extern sine(complex[float[size]] amp, duration  d, float[size] frequency, angle[size] phase) -> waveform;

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
only appear inside a ``defcal`` block and have two required parameters:

- A value of type ``waveform`` representing the waveform envelope.
- The frame to use for the pulse.

Here, the ``frame`` provides both time at which the ``waveform`` envelope is scheduled (i.e. via the frame ``.time``
attribute), its carrier frequency (i.e. via the frames ``.frequency`` attribute), and its phase offset (i.e. via
the frame ``.phase`` attribute).

.. code-block:: javascript

  play(waveform wfm, frame fr)

For example,

.. code-block:: javascript

  defcal play_my_pulses $0 {
    // Play a 3 sample pulse on the tx0 port
    play([1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j], driveframe);

    // Play a gaussian pulse on the tx1 port
    frame f1 = newframe(tx1, q1_freq, 0.0);
    play(gaussian(...), f1);
  }

If the ``waveform`` duration is not realizable by the sample rate of the associated ``port``,
the compiler shall raise a compile-time error.


Capture Instruction
-------------------

Acquisition is scheduled by a ``capture`` instruction. This is a special
``extern`` function which is specified by a hardware vendor. The measurement
process is difficult to describe generically due to the wide variety of
hardware and measurement methods. Like the ``play`` instruction, these instructions
may only appear inside a ``defcal`` or ``cal`` block.

The minimum requirement for a ``capture`` command is that the ``frame`` provides the time at
which data is captured. As such, the only required parameter for a ``capture`` instruction
is a ``frame``.

However, the following are possible parameters that might also be included:

- A "duration" of type ``duration``, if it cannot be inferred from other parameters.
- A "filter" of type ``waveform``, which is dot product-ed with the measured IQ to distill the
  result into a single IQ value

Again it is up to the hardware vendor to determine the parameters and write a
extern definition at the top-level, such as:

.. code-block:: javascript

   // Minimum requirement
   extern capture(frame output);

   // A capture command that returns an iq value
   extern capture(waveform filter, frame output) -> complex[32];

   // A capture command that returns a discrimnated bit
   extern capture(waveform filter, frame output) -> bit;

   // A capture command that returns a raw waveform data
   extern capture(duration len, frame output) -> waveform;

   // A capture that returns a count e.g. number of photons detected
   extern capture(duration len, frame output) -> int

The return type of a ``capture`` command varies. It could be a raw trace, ie., a
list of samples taken over a short period of time. It could be some averaged IQ
value. It could be a classified bit. Or it could even have no return value,
pushing the results into some buffer which is then accessed outside the program.

For example, the ``capture`` instruction could return raw waveform data that is then
discriminated using user-defined boxcar and discrimination ``extern``\s.

.. code-block:: javascript

    // Use a boxcar function to generate IQ data from raw waveform
    extern boxcar(waveform input) -> complex[float[64]];
    // Use a linear discriminator to generate bits from IQ data
    extern discriminate(complex[float[64]] iq) -> bit;

    cal {
        // Define the ports
        extern port m0;
        extern port cap0;
    }

    defcal measure $0 -> bit {

        // Force time of carrier to 0 for consistent phase for discrimination.
        frame stimulus_frame = newframe(m0, 5e9, 0);
        frame capture_frame = newframe(cap0, 5e9, 0);

        // Measurement stimulus envelope
        waveform meas_wf = gaussian_square(1.0, 16000dt, 262dt, 13952dt);

        // Play the stimulus
        play(meas_wf, stimulus_frame);

        // Align measure and capture frames
        barrier stimulus_frame, capture_frame;

        // Capture transmitted data after interaction with measurement resonator
        // extern capture(duration duration, frame capture_frame) -> waveform;
        waveform raw_output = capture(16000dt, capture_frame);

        // Kernel and discriminate
        complex[float[32]] iq = boxcar(raw_output);
        bit result = discriminate(iq);

        return result;
    }

If the ``duration`` argument or the ``waveform`` duration are not realizable by the sample rate of
the associated ``port``, the compiler shall raise a compile-time error.

Timing
------

Each frame maintains its own "clock" of type ``duration``, which can only be manipulated implicitly
through the existing timing instructions of ``delay``, ``play``, ``capture``,  and ``barrier``.

Initial Time
~~~~~~~~~~~~~

As briefly discussed in the :ref:`Frame Initialization` section, a ``frame`` initialized via a
``newframe`` command has its ``.time`` set to the time at the beginning of the containing
``cal`` or ``defcal`` block. Since a ``cal`` block is globally scoped in OpenPulse, this time
would be absolute 0. Meanwhile, a ``defcal``s start time is determined by when it is scheduled
(see :ref:`Timing` section for more details) e.g.

.. code-block:: javascript

  ...

  cal {
    extern port d0;
    // initialized with absolute time 0 because `cal` is global scope
    frame driveframe1 = newframe(d0, 5.0e9, 0.0);
    waveform wf = gaussian(0.5, 16ns, 4ns);
  }

  defcal my_gate1 $0 {
    play(wf, driveframe1);
  }

  defcal my_gate2 $0 {
    // initialized to time at beginning of `my_gate2`
    frame driveframe2 = newframe(d0, 5.0e9, 0.0);
    play(wf, driveframe2);
  }

  defcal my_gate3 $0 {
    // initialized to time at beginning of `my_gate3`
    frame driveframe3 = newframe(d0, 5.0e9, 0.0);
    play(wf, driveframe3);
  }

  // driveframe1.time = 0ns when `play(wf, driveframe1)` is issued, advances to 16ns after `play`
  my_gate1 $0;
  // driveframe2.time = 16ns when initialized via `newframe`
  my_gate2 $0;
  // driveframe3.time = 32ns when initialized via `newframe`
  my_gate3 $0;

Delay
~~~~~

When a ``delay`` instruction is issued for a list of ``frame``\s, the ``frame`` clocks advance
by the requested duration.

.. code-block:: javascript

  ...

  // driveframe advances by 13ns
  delay[13ns] driveframe;

If the ``duration`` argument of the delay is not realizable by the sample rate of
the underlying ``port``, the compiler shall raise a compile-time error.

Play and Capture
~~~~~~~~~~~~~~~~~~

When a ``play`` or ``capture`` instruction is issued, the ``frame`` clock advances
by the duration of the associated ``waveform`` argument.

.. code-block:: javascript

  ...

  cal {
    extern port d0;
    frame driveframe = newframe(d0, 5.0e9, 0.0);
    waveform wf = gaussian(0.5, 16ns, 4ns);
  }

  delay[13ns] driveframe;
  // driveframe.time is now 13ns

  play(wf, driveframe);
  // driveframe.time is now 29ns

Barrier
~~~~~~~~

When a ``barrier`` instruction is issued for a list of ``frame``\s, the ``frame`` clocks are
aligned to the latest time of the all ``frame``\s listed.

.. code-block:: javascript

  cal {
    extern port d0;
    extern port d1;

    driveframe1 = newframe(d0, 5.1e9, 0.0);
    driveframe2 = newframe(d1, 5.2e9, 0.0);

    delay[13ns] driveframe1;

    // driveframe1.time == 13ns, driveframe2.time == 0ns

    // Align frames
    barrier driveframe1, driveframe2;

    // driveframe1.time == driveframe2.time == 13ns
  }

Moreover, ``defcal`` blocks have an implicit ``barrier`` on every frame enters the block e.g.

.. code-block:: javascript

  cal {
    extern port tx0;
    extern port tx1;
    waveform p = ...; // some 100ns waveform
    frame driveframe1 = newframe(tx0, 5.0e9, 0);
    frame driveframe2 = newframe(tx1, 6.0e9, 0);
  }

  defcal two_qubit_gate $1 $2 {
    // implicit: barrier driveframe1, driveframe2;
    play(wf, driveframe1);
    play(wf, driveframe2);
  }

  defcal single_qubit_gate $1 {
    // implicit: barrier driveframe1;
    play(wf, driveframe1);
  }

  single_qubit_gate $1;
  // Implicit alignment of `driveframe1` and `driveframe2` when entering `two_qubit_gate` block
  two_qubit_gate $1 $2;


Phase tracking
~~~~~~~~~~~~~~

As discussed in the :ref:`Frame Manipulation` section, the accrued phase of a frame can be manipulated
throughout a program by referencing ``.phase``. The phase is also implicitly manipulated when the time
of the frame is advanced using a ``delay``, ``play``, or ``capture`` instruction e.g.

.. code-block:: javascript

  cal {
    extern port tx0;
    waveform p = ...; // some 100ns waveform

    // Frame initialized with accured phase of 0
    frame driveframe0 = newframe(tx0, 5.0e9, 0);
  }

  defcal single_qubit_gate $0 {
    play(wf, driveframe0);
  }

  defcal single_qubit_delay $0 {
    delay[13ns] driveframe0;
  }

  // driveframe0.phase = 0
  single_qubit_gate $0;
  // Implicit advancement: driveframe0.phase += 2π * driveframe0.frequency * durationof(wf)
  //                                         += 2π * 5e9 * 100e-9

  // Change the frequency
  cal {
    driveframe0.frequency = 6e9;
  }

  single_qubit_delay $0;
  // Implicit advancement: driveframe0.phase += 2π * driveframe0.frequency * 13e-9
  //                                         += 2π * 6e9 * 13e-9



This is a key property required for pulses to be defined in the rotating frame with the effect
being an equivalent application in the lab frame.

Collisions
~~~~~~~~~~~~~~~~~

If a frame is scheduled or referenced simultaneously in two ``defcal`` or ``cal`` blocks, it is
considered a compile-time error e.g.

.. code-block:: javascript

  ...

  defcal single_qubit_gate $0 {
    play(wf, driveframe1);
  }

  defcal single_qubit_gate $1 {
    play(wf, driveframe1);
  }

  ...

  // Compile-time error when requesting parallel usage of the same frame
  single_qubit_gate $0 $1;

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

  // define a long saturation pulse of a set duration and amplitude
  defcal saturation_pulse $0 {
      // assume frame can be linked from a vendor supplied `cal` block
      play(constant(0.1, 100e-6), driveframe);
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
          // assume frame can be linked from a vendor supplied `cal` block
          play(wf, driveframe);
      }
      measure $0;
  }

Cross-resonance gate
~~~~~~~~~~~~~~~~~~~~


.. code-block:: javascript

  cal {
     // Access globally (or externally) defined ports
     extern port d0;
     extern port d1;
     frame frame0 = newframe(d0, 5.0e9, 0);
  }

  defcal cross_resonance $0, $1 {
      waveform wf1 = gaussian_square(1., 1024dt, 128dt, 32dt);
      waveform wf2 = gaussian_square(0.1, 1024dt, 128dt, 32dt);

      /*** Do pre-rotation ***/

      // generate new frame for second drive that is locally scoped
      // initialized to time at the beginning of `cross_resonance`
      frame temp_frame = newframe(d1, frame0.frequency, frame0.phase);

      play(wf1, frame0);
      play(wf2, temp_frame);

      /*** Do post-rotation ***/

  }

Geometric gate
~~~~~~~~~~~~~~

.. code-block:: javascript

  cal {
      extern port dq;
      float fq_01 = 5e9; // hardcode or pull from some function
      float anharm = 300e6; // hardcode or pull from some function
      frame frame_01 = newframe(dq, fq_01, 0);
      frame frame_12 = newframe(dq, fq_01 + anharm, 0);
  }

  defcal geo_gate(angle[32] theta) $q {
      // theta: rotation angle (about z-axis) on Bloch sphere

      // Assume we have calibrated 0->1 pi pulses and 1->2 pi pulse
      // envelopes (no sideband)
      waveform X_01 = {...};
      waveform X_12 = {...};
      float[32] a = sin(theta/2);
      float[32] b = sqrt(1-a**2);

      // Double-tap
      play(scale(a, X_01), frame_01);
      play(scale(b, X_12), frame_12);
      play(scale(a, X_01), frame_01);
      play(scale(b, X_12), frame_12);
  }

Neutral atoms
~~~~~~~~~~~~~

In this example, the signal chain is composed of two electro-optic modulators (EOM) and
an acousto-optic deflector (AOD). The EOMs put sidebands on the laser light while the AOD diffracts
the light in an amount proportional to the frequency of the RF drive. This example was chosen
because it is similar in spirit to the work by Levine et al._:cite:`levine2019` except that phase
control is exerted using virtual Z gates on the AODs -- requiring frame tracking of the qubit
frequency yet application of a tone that maps to the qubit position (i.e. requires the use of a
sideband).

The program aims to perform a Hahn echo sequence on q1, and a Ramsey sequence on q2 and q3.

.. code-block:: javascript

  // Raman transition detuning Δ from the  5S1/2 to 5P1/2 transition
  const float Δ = ...;

  // Hyperfine qubit frequency
  const float qubit_freq = ...;

  // Positional frequencies for the AODS to target the specific qubit
  const float q1_pos_freq = ...;
  const float q2_pos_freq = ...;
  const float q3_pos_freq = ...;

  // Calibrated amplitudes and durations for the Raman pulses supplied via the AOD envelopes
  const float q1_π_half_amp = ...;
  const float q2_π_half_amp = ...;
  const float q3_π_half_amp = ...;
  const duration π_half_time = ...;

  // Time-proportional phase increment
  const float tppi_1 = ...;
  const float tppi_2 = ...;
  const float tppi_3 = ...;


  cal {
    extern port eom_a_port;
    extern port eom_b_port;
    extern port aod_port;

    // Define the Raman frames, which are detuned by an amount Δ from the  5S1/2 to 5P1/2 transition
    // and offset from each other by the qubit_freq
    frame raman_a_frame = newframe(eom_a_port, Δ, 0.0);
    frame raman_b_frame = newframe(eom_b_port, Δ-qubit_freq, 0.0);

    // Three frames to phase track each qubit's rotating frame of reference at it's frequency
    frame q1_frame = newframe(aod_port, qubit_freq, 0)
    frame q2_frame = newframe(aod_port, qubit_freq, 0)
    frame q3_frame = newframe(aod_port, qubit_freq, 0)

    // Generic gaussian envelope
    waveform π_half_sig = gaussian(..., π_half_time, ...);

    // Waveforms ultimately supplied to the AODs. We mix our general Gaussian pulse with a sine wave to
    // put a sideband on the outgoing pulse. This helps us target the qubit position while maintainig the
    // desired Rabi rate.
    waveform q1_π_half_sig = mix(π_half_sig, sine(q1_π_half_amp, π_half_time, q1_pos_freq-qubit_freq, 0.0));
    waveform q2_π_half_sig = mix(π_half_sig, sine(q2_π_half_amp, π_half_time, q2_pos_freq-qubit_freq, 0.0));
    waveform q3_π_half_sig = mix(π_half_sig, sine(q3_π_half_amp, π_half_time, q3_pos_freq-qubit_freq, 0.0));
  }

  // π/2 pulses on all three qubits
  defcal rx(π/2) $1 $2 $3 {
        // Simultaneous π/2 pulses
        play(constant(raman_a_amp, π_half_time) , raman_a_frame);
        play(constant(raman_b_amp, π_half_time) , raman_b_frame);
        play(q1_π_half_sig, q1_frame);
        play(q2_π_half_sig, q2_frame);
        play(q3_π_half_sig, q3_frame);
  }

  // π/2 pulse on only qubit $2
  defcal rx(π/2) $2 {
      play(constant(raman_a_amp, π_half_time) , raman_a_frame);
      play(constant(raman_b_amp, π_half_time) , raman_b_frame);
      play(q2_π_half_sig, q2_frame);
  }

  // Ramsey sequence on qubit 1 and 3, Hahn echo on qubit 2
  for τ in [0:10us:1ms] {

    // First π/2 pulse
    rx(π/2) $0, $1, $2;

    // First half of evolution time
    cal {
      delay[τ/2] raman_a_frame raman_b_frame q1_frame q2_frame q3_frame;
    }

    // Hahn echo π pulse composed of two π/2 pulses
    for ct in [0:1]:
      rx(π/2) $2;

    cal {
      // Align all frames
      barrier raman_a_frame raman_b_frame q1_frame q2_frame q3_frame;

      // Second half of evolution time
      delay[τ/2] raman_a_frame raman_b_frame q1_frame q2_frame q3_frame;

      // Time-proportional phase increment signals different amount
      q1_frame.phase += tppi_1 * τ;
      q2_frame.phase += tppi_2 * τ;
      q3_frame.phase += tppi_3 * τ;
    }

    // Second π/2 pulse
    rx(π/2) $0, $1, $2;

Multiplexed readout and capture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we want to perform readout and capture of a pair of qubits, but mediated by a
single physical transmission and capture port. The example is for just two qubits, but works the same for
many (just adding more frames, waveforms, plays, and captures).

.. code-block:: javascript

  const duration electrical_delay = ...;
  const float q0_ro_freq = ...;
  const float q1_ro_freq = ...;

  cal {
    // the transmission/captures ports are the same for $0 and $1
    extern port ro_tx;
    extern port ro_rx;

    // readout stimulus and capture frames of different frequencies
    frame q0_stimulus_frame = newframe(ro_tx, q0_ro_freq, 0);
    frame q0_capture_frame = newframe(ro_rx, q0_ro_freq, 0);
    frame q1_stimulus_frame = newframe(ro_tx, q1_ro_freq, 0);
    frame q1_capture_frame = newframe(ro_rx, q1_ro_freq, 0);
  }

  defcal multiplexed_readout_and_capture $0, $1 -> bit[2] {
      bit[2] b;

      // flat-top readout waveforms
      waveform q0_ro_wf = constant(amp=0.1, d=...);
      waveform q1_ro_wf = constant(amp=0.2, d=...);

      // multiplexed readout
      play(q0_ro_wf, q0_stimulus_frame);
      play(q1_ro_wf, q1_stimulus_frame);

      // simple boxcar kernel
      waveform ro_kernel = constant(amp=1, d=...);

      barrier q0_stimulus_frame q1_stimulus_frame q0_capture_frame q1_capture_frame;
      delay[electrical_delay] q0_capture_frame q1_capture_frame;

      // multiplexed capture
      // extern capture(waveform ro_kernel, frame capture_frame) -> bit;
      b[1] = capture(ro_kernel, q0_capture_frame);
      b[2] = capture(ro_kernel, q1_capture_frame);

      return b;
  }

Open Questions
~~~~~~~~~~~~~~

- How do we handle mapping wildcarded qubits to arbitrary pulse-level resources?
- Is timing on frames, and ports as resources clear?
- How will hardware attributes be handled?
