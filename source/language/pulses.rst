.. role:: raw-latex(raw)
   :format: latex
..

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
and measurement using a text representation of OpenPulse.

The entry point to such gate and measurement definitions is the ``defcal`` keyword
analogous to the ``gate`` keyword, but where the ``defcal`` body specifies a pulse-level
instruction sequence on *physical* qubits, e.g.

.. code-block:: c

   defcal rz(angle[20]:theta) %q { ... }
   defcal measure %q -> bit { ... }

We distinguish gate and measurement definitions by the presence of a
return value type in the latter case, analogous to the subroutine syntax
defined earlier. The reference to *physical* rather than *virtual*
qubits is critical because quantum registers are no longer
interchangeable at the pulse level. Due to varying physical qubit
properties a microcode definition of a gate on one qubit will not
perform the equivalent operation on another qubit. To meaningfully
describe gates as pulses we must bind operations to specific qubits.
QASM achieves this by prefixing qubit references with ``%`` to indicate
a specific qubit on the device, e.g. ``%2`` would refer to physical
qubit 2, while ``%q`` is an unbound reference to a physical qubit.

As a consequence of the need for specialization of operations on
particular qubits, we expect the same symbol to be defined multiple
times, e.g.

.. code-block:: c

   defcal h %0 { ... }
   defcal h %1 { ... }

and so forth. Some operations require further specialization on
parameter values, so we also allow multiple declarations on the same
physical qubits with different parameter values, e.g.

.. code-block:: c

   defcal rx(pi) %0 { ... }
   defcal rx(pi / 2) %0 { ... }

Given multiple definitions of the same symbol, the compiler will match
the most specific definition found for a given operation. Thus, given,

#. ``defcal rx(angle[20]:theta) %q  ...``

#. ``defcal rx(angle[20]:theta) %0  ...``

#. ``defcal rx(pi / 2) %0  ...``

the operation ``rx(pi/2) %0`` would match to (3), ``rx(pi) %0`` would
match (2), ``rx(pi/2) %1`` would match (1).

Note that ``defcal`` and ``gate`` communicate orthogonal information to the compiler. ``gate``'s
define unitary transformation rules to the compiler. The compiler may
freely invoke such rules on operations while preserving the structure of
a circuit as a collection of ``gate``'s and ``subroutine``'s. The ``defcal`` declarations instead define
elements of a symbol lookup table. As soon as the compiler replaces a ``gate``
with a ``defcal`` definition, we have changed the fundamental structure of the
circuit. Most of the time symbols in the ``defcal`` table will also have
corresponding ``gate`` definitions. However, if a user provides a ``defcal`` for a symbol
without a corresponding ``gate``, then we treat such operations like the ``opaque`` gates
of prior versions of OpenQASM.

OpenPulse instructions
======================

In addition to OpenQASM instructions, ``defcal`` blocks may contain OpenPulse 
instructions using a text-based version of OpenPulse defined here. OpenPulse is 
a JSON format described in the paper 
`Qiskit Backend Specifications for OpenQASM and OpenPulse Experiment <https://arxiv.org/abs/1809.03452>`_.

The text format described here has several advantages over the equivalent JSON 
format:

- It is more readable
- Absolute time is handled through built-in timekeeping instructions
- Gates and classical instructions can be mixed in with the pulses to create far richer calibrations

Channels
--------

Channels (sometimes referred to as "frames") describe the different forms of
classically-controlled stimulus fields used to interact with a qubit. There are
two kinds of channels: input channels, which send signal into the system to
drive the qubit, and output channels, which measure signal from the system to
measure qubits.

Each channel has a user-specified local oscillator frequency which is assumed to
have been specified outside of the context of OpenQASM.

A value of type ``channel`` can be retrieved with the ``drive`` (input channels) 
and ``acquire`` (output channels) functions, a reference to the physical qubit, 
and the name of the channel. If the name of the channel is omitted then the
names "drive" and "acquire" will be used respectively.

.. code-block:: none

   // Get the drive input channel for qubit 0
   drive(%0)
   // Get the acquire output channel for qubit 1
   acquire(%1)
   // Get an input channel named "measure" for qubit 1
   // Could be used to specify the measurement stimulus channel
   drive(%1, "measure")
   // Get a custom input channel named "cr1" for qubit 0
   drive(%0, "cr1")

Play instruction
----------------

Pulses are scheduled using the ``play`` instruction. Play instructions have two
required parameters:
- the channel on which to play the pulse
- an array of complex samples which define the amplitude points for the pulse envelope

The length of the pulse will be the length of the array multiplied by the unit
``dt``, which specifies the sample rate.

.. code-block:: none

   // Play a 3 sample pulse on qubit 0's drive channel
   play drive(%0), [1+0*j, 0+1*j, 1/sqrt(2)+1/sqrt(2)*j];

Specifying a full list of samples for real-life pulses can be unwieldy, so we
include several built-in pulse shape functions as well:

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

Shift Phase Instruction
-----------------------

A ``shift_phase`` instruction schedules a phase advance for all the following
pulses on that channel. This is equivalent to multiplying each pulse by
:math:`e^{-i*\theta}`, where theta is the phase change in radians.

The ``shift_phase`` instruction takes two parameters, a channel and the
requested phase change of type angle. The exact precision of the implemented
phase change will vary depending on hardware support.

.. code-block:: none

   // Shift phase of qubit 0 by pi/4, eg. an rz gate with angle -pi/4
   shift_phase drive(%0), pi/4;

   // Define a calibration for the rz gate on all physical qubits
   defcal rz(angle[20]:theta) %q {
     shift_phase drive(%q), -theta;
   }

Shift Frequency Instruction
---------------------------

A ``shift_freq`` instruction schedules a frequency advance for all the following
pulses on that channel. This is useful for defining spectroscopy experiments.

The ``shift_freq`` instruction takes two parameters, a channel and the
requested frequency change of type float in units of GHz.

Here's an example qubit spectroscopy experiment. Note that the starting
frequency will be defined somewhere outside OpenQASM.

.. code-block:: none

   qubit q;

   const shots = 1000;
   const dfreq = 0.001; # 1MHz per point
   const points = 50; # Sweep over 50MHz

   complex[float[32]] iq, average;
   complex[float[32]] output[points];

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

   defcal shift %q {
     shift_freq drive(%q) dfreq;
   }

Capture Instruction
-------------------

Acquisition is scheduled by a ``capture`` instruction.

The ``capture`` instruction takes two parameters, a channel and the filter to
apply to the returned signal. The length of the filter in dt will determine how
long the capture channel is open. The ``capture`` instruction returns the dot
product of the measured IQ values and the filter. (Note that the filter is
sometimes referred to as "kernel" in other contexts, but this is not related in
any way to the ``kernel`` instruction in OpenQASM).

.. code-block:: none
    
   complex[float[32]] filter = [1, 1, 1, 1, 1];
   // Capture for 5 samples
   iq = capture acquire(%0), filter;

Specifying a full list of samples for real-life filters can be unwieldy, so we
include several built-in filter functions as well. Note that these return the
same type as pulse shape functions and therefore either can be used for pulse 
shapes and filters.

.. code-block:: none

   // Define a boxcar (aka. constant) filter of length l
   boxcar(l:length)

Timing
------

Each channel maintains its own "clock". When a pulse is played the clock for 
that channel advances by the number of samples in the pulse. The same is true
for output channels based on the length of the capture filter. Pulses on a
single channel cannot be played simultaneously, although pulses on multiple
channels for the same qubit can.

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

   complex[float[32]] pulse[100] = [...];

   defcal simultaneous_pulsed_gate %0 {
     play drive(%0, "channel1"), pulse;
     delay[20dt] drive(%0, "channel2");
     // Starts the 100dt pulse 20dt into "channel1" already playing it
     play drive(%0, "channel2"), pulse;
   }