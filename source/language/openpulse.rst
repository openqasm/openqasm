OpenPulse Grammar
=================

In addition to OpenQASM instructions, ``defcal`` blocks may contain OpenPulse 
instructions. Or equivalently stated: OpenPulse instructions cannot appear
outside of a ``defcal`` block.

These instructions are motivated by the original OpenPulse specification which
was defined as a JSON wire-format for pulse-level quantum programs in the paper
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment <https://arxiv.org/abs/1809.03452>`_. 
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
for use by end users. Each channel may also have associated static settings,
such as local-oscillator frequencies, which do not vary throughout program
execution. Again it is expected that vendors of quantum hardware provide a
method for manipulating those static settings if appropriate.

There are two kinds of channels: transmit channels (sending input to a quantum
device) and receive channels (reading output from a quantum device).

The ``channel`` type is a compile-time type representing a channel.

A value of type ``channel`` is retreived with the special functions
``transmit`` and ``receive``. These functions take an optional string argument
followed by 1 or more physical qubits.

The hardware vendor, during compilation, will substitute valid calls to
``transmit`` and ``receive`` with their corresponding channels.

A recommended convention: calling ``transmit`` with a single qubit argument
should return the channel for driving single qubit gates, and calling
``receive`` with a single qubit argument should return the channel for reading
out the state of that qubit.

.. code-block:: none

   // Get the default input channel for qubit 0
   transmit(%0)
   // Get the default output channel for qubit 1
   receive(%1)
   // Get an input channel named "measure" for qubit 1
   // Could be used to specify the measurement stimulus channel
   transmit("measure", %1)
   // Get an output channel named "cr1" for qubit 0
   receive("cr1", %0)
   // Get the default output channel for qubits 0 and 1
   receive(%0, %1)

Frames
------

It turns out to be quite useful to keep track of a set of carrier signals
throughout the execution of a program. These carrier signals are called "frames"
and are defined by :math:$A*e^{i\left(2\pi f t + \theta\right)}$, where `f` is
frequency, `theta` is phase, and `A` is a scaling factor.

Frames are attached to channels by a 1:1 correspondence. Every frame must 
specify a frequency before any pulses can be played on that channel. The special 
``prelude`` defcal is a good place to place these instructions.

.. code-block:: none

   defcal prelude {
      // Required: set the frequency to 5GHz
      initframe transmit(%1), 5e9;
      // Optional: set the starting phase (otherwise it would start at 0)
      set_phase transmit(%1), pi;
   }

Frames track the set of (frequency, phase, scale) throughout the program and 
are manipulated using the following `set_` and `shift_` commands. Then when
a pulse is played the carrier signal of the frame is mixed with the pulse itself
to create the final signal which will be applied on the channel.

Frequency has no default since it must be set at the beginning. Phase defaults
to 0 and is a value of type ``angle``. Scale defaults to 1.0 and is a value of
type ``float``. The exact precision of these three parameters is hardware
specific.

frameof command
~~~~~~~~~~~~~~~

The ``frame`` type is a compile-time type represnting a frame. It is useful
when playing a pulse using the frame of a different channel.

A value of type ``frame`` is retrieved by calling the ``frameof`` command
and passing in a channel.

Frame manipulation
~~~~~~~~~~~~~~~~~~

The (frequency, phase, scale) of a frame can be manipulated throughout program
execution with the following instructions. After a call to one of these
instructions, future references to that frame will have the new value.

All of the following instructions have the same form. The first parameter can 
either be a ``frame`` type or a ``channel`` type (in which case the 
corresponding frame will be used). The second parameter is the value to shift
or set. It must be the appropriate type, ``float`` for frequency, ``angle`` for
phase, and ``float`` for scale. Again, the exact precision of these calculations
is hardware specific.

The relevant instructions are:

- ``set_frequency`` and ``shift_frequency``
- ``set_phase`` and ``shift_phase``
- ``set_scale`` and ``shift_scale``

Here's an example of using ``shift_scale`` to calibrate an ``rz`` gate:

.. code-block:: none

   // Shift phase of qubit 0's frame by pi/4, eg. an rz gate with angle -pi/4
   shift_phase transmit(%0), pi/4;

   // Equivalent, but more verbose
   frame fr = frameof(transmit(%0));
   shift_phase fr, pi/4;

   // Define a calibration for the rz gate on all physical qubits
   defcal rz(angle[20]:theta) %q {
     shift_phase transmit(%q), -theta;
   }

Here's an example qubit spectroscopy experiment.

.. code-block:: none

   qubit q;

   const shots = 1000;
   const dfreq = 1e6; # 1MHz per point
   const points = 50; # Sweep over 50MHz

   complex[32] iq, average;
   complex[32] output[points];

   for p in [0 : points-1] {
     average = 0;
     for i in [0 : shots-1] {
       // Assumes suitable calibrations for reset, x, and measure_iq
       reset q;
       x q;
       measure_iq q -> iq;

       average = (average * i + iq) / (i + 1);
     }
     shift q;
     output[p] = average;
   }

   defcal prelude {
      set_frequency transmit(%q) 5e9;
   }

   defcal shift %q {
     shift_frequency transmit(%q) dfreq;
   }

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

   // Define a boxcar (aka. constant) pulse of length l
   boxcar(l:length)

Play instruction
~~~~~~~~~~~~~~~~

Pulses are scheduled using the ``play`` instruction. Play instructions have two
required parameters:

- the channel on which to play the pulse
- a value of type ``pulse`` representing the pulse envelope

Optionally the ``play`` instruction can also take a third parameter: the frame
to use for the pulse. If the frame is not specified then the corresponding frame
for the channel will be used instead, as if ``frameof`` was called for that
channel.

.. code-block:: none

   // Play a 3 sample pulse on qubit 0
   play transmit(%0), [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j];

   // Play a gaussian on qubit 0 using qubit 1's frame
   frame f1 = frameof(transmit(%1));
   play transmit(%0), gaussian(...), f1;

Capture Instruction
-------------------

Acquisition is scheduled by a ``capture`` instruction. This is a special
``kernel`` function which is specified by a hardware vendor. The measurement
process is difficult to describe generically due to the wide variety of
hardware and measurement methods.

The only required parameter is an ``channel``, ie. a channel returned from
calling the ``receive`` function.

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
   kernel capture(channel output) -> complex[32];

   // A capture command with more features
   kernel capture(channel output, pulse filter) -> complex[32];

The return type of a ``capture`` command varies. It could be a raw trace, ie a
list of samples taken over a short period of time. It could be some averaged IQ
value. It could be a classified bit. Or it could even have no return value,
pushing the results into some buffer which is then accessed outside the program.

Timing
------

Each channel maintains its own "clock". When a pulse is played the clock for 
that channel advances by the length of the pulse. The same is true
for output channels. Pulses on a single channel cannot be played simultaneously,
although pulses on multiple channels for the same qubit can.

For channels, everything behaves analogous to qubits in the 
`Delays <delays.html>`_ section of this specification. There are however some
small differences.

The ``delay`` instruction may take a channel instead of a qubit. If a ``delay``
instruction is applied to the qubit, this is the same as applying the delay to
all channels on the qubit simultaneously.

The ``barrier`` instruction on a qubit implies a barrier on all channels defined
for that qubit. A barrier instruction will advance the clocks on all channels of
the qubit to the channel with the highest clock.

``defcal`` blocks have an implicit barrier on every qubit argument, meaning
that clocks are guaranteed to be aligned at the start of the ``defcal`` block.
These blocks also need to have a well-defined length, similar to the ``boxas``
block.

.. code-block:: none

   pulse p = ...;

   defcal simultaneous_pulsed_gate %0 {
     play transmit("channel1", %0), p;
     delay[20dt] transmit("channel2", %0);
     // Starts the 100dt pulse 20dt into "channel1" already playing it
     play transmit("channel1", %0), pulse;
   }