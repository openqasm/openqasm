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
instead works with abstract "frames", described below. The static settings above 
should also include a mapping of these abstract frames to the correct channels.

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

Each frame maintains its own "clock". When a pulse is played the clock for 
that frame advances by the length of the pulse. 

For frames, everything behaves analogous to qubits in the 
`Delays <delays.html>`_ section of this specification. There are however some
small differences.

The ``delay`` instruction may take a frame instead of a qubit. The ``barrier`` 
instruction may also take a list of frames intead of a list of qubits.

``defcal`` blocks have an implicit barrier on every frame used within the block,
meaning that clocks are guaranteed to be aligned at the start of the block.
These blocks also need to have a well-defined length, similar to the ``boxas``
block.

.. code-block:: none

   pulse p = ...; // some 100dt pulse

   defcal simultaneous_pulsed_gate %0 {
     play(p) frameof("drive0", %0);
     delay[20dt] frameof("drive1", %0);
     // Starts the 100dt pulse 20dt into "drive0" already playing it
     play(p) frameof("drive1");
   }
