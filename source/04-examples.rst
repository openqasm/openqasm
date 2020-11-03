Examples
========

This section gives several examples of quantum circuits expressed in
OpenQASM (version 3). The circuits use a gate basis defined for the
Quantum Experience.

Standard gates
--------------

A collection of standard gates are defined in a header file . We define
these standard gates in terms of the abstract gates and . Choosing to
use abstract gates to define additional gates in the library gives some
flexibility to add or change the gate library at a later time without
changing OpenQASM.

.. code:: c

   // Standard gate library

   // phase gate (Z-rotation by lambda)
   gate phase(angle[32]:lambda) q { U(0, 0, lambda) q; }
   // controlled-NOT
   gate cx c, t { CX c, t; }
   // idle gate (identity)
   gate id a { U(0, 0, 0) a; }
   // Pauli gate: bit-flip
   gate x a { U(pi, 0, pi) a; }
   // Pauli gate: bit and phase flip
   gate y a { U(pi, pi / 2, pi / 2) a; }
   // Pauli gate: phase flip
   gate z a { phase(pi) a; }
   // Clifford gate: Hadamard
   gate h a { U(pi / 2, 0, pi) a; }
   // Clifford gate: sqrt(Z) phase gate
   gate s a { phase(pi / 2) a; }
   // Clifford gate: conjugate of sqrt(Z)
   gate sdg a { phase(-pi / 2) a; }
   // C3 gate: sqrt(S) phase gate
   gate t a { phase(pi/4) a; }
   // C3 gate: conjugate of sqrt(S)
   gate tdg a { phase(-pi/4) a; }
   // Rotation around X-axis
   gate rx(angle[32]:theta) a { U(theta, -pi / 2, pi / 2) a; }
   // rotation around Y-axis
   gate ry(angle[32]:theta) a { U(theta, 0, 0) a; }
   // rotation around Z axis
   gate rz(angle[32]:phi) a { phase(phi) a; }
   // controlled-Phase
   gate cz a, b { h b; cx a, b; h b; }
   // controlled-Y
   gate cy a, b { sdg b; cx a, b; s b; }
   // controlled-H
   gate ch a, b {
     h b;
     sdg b;
     cx a, b;
     h b;
     t b;
     cx a, b;
     t b; s a;
     h b;
     s b;
     x b;
   }
   // Toffoli
   gate ccx a, b, c
   {
     h c;
     cx b, c;
     tdg c;
     cx a, c;
     t c;
     cx b, c;
     tdg c;
     cx a, c;
     t b; t c; h c;
     cx a, b;
     t a; tdg b;
     cx a, b;
   }
   // controlled-swap
   gate cswap a, b, c
   {
     cx c, b;
     ccx a, b, c;
     cx c, b;
   }
   // controlled-rz
   gate crz(angle[32]:lambda) a, b
   {
     phase(lambda / 2) b;
     cx a, b;
     phase(-lambda / 2) b;
     cx a, b;
   }
   // controlled-phase
   gate cphase(angle[32]:lambda) a, b
   {
     phase(lambda / 2) a;
     cx a, b;
     phase(-lambda / 2) b;
     cx a, b;
     phase(lambda / 2) b;
   }
   // controlled-U
   gate cu(angle[32]:theta,angle[32]:phi,angle[32]:lambda) c, t
   {
     // implements controlled-U(theta,phi,lambda) with  target t and control c
     phase((lambda - phi)/2) t;
     cx c,t;
     U(-theta / 2, 0, -(phi + lambda) / 2) t;
     cx c, t;
     U(theta / 2, phi, 0) t;
   }

Quantum teleportation
---------------------

Quantum teleportation
(Fig. `[fig:example:teleport] <#fig:example:teleport>`__) demonstrates
conditional application of future gates based on prior measurement
outcomes.

.. code:: c

   // quantum teleportation example
   OPENQASM 3;
   include "stdgates.inc";
   qubit q[3];
   bit c0;
   bit c1;
   bit c2;
   // optional post-rotation for state tomography
   // empty gate body => identity gate
   gate post q { }
   reset q;
   u3(0.3, 0.2, 0.1) q[0];
   h q[1];
   cx q[1], q[2];
   barrier q;
   cx q[0], q[1];
   h q[0];
   c0 = measure q[0];
   c1 = measure q[1];
   if(c0==1) z q[2];
   if(c1==1) { x q[2]; }  // braces optional in this case
   post q[2];
   c2 = measure q[2];

Quantum Fourier transform
-------------------------

The quantum Fourier transform (QFT,
Fig. `[fig:example:qft] <#fig:example:qft>`__) demonstrates parameter
passing to gate subroutines. This circuit applies the QFT to the state
:math:`|q_0 q_1 q_2 q_3\rangle=|1010\rangle` and measures in the
computational basis.

.. code:: c

   // quantum Fourier transform
   OPENQASM 3;
   include "stdgates.inc";
   qubit q[4];
   bit c[4];
   reset q;
   x q[0];
   x q[2];
   barrier q;
   h q[0];
   cphase(pi / 2) q[1], q[0];
   h q[1];
   cphase(pi / 4) q[2], q[0];
   cphase(pi / 2) q[2], q[1];
   h q[2];
   cphase(pi / 8) q[3], q[0];
   cphase(pi / 4) q[3], q[1];
   cphase(pi / 2) q[3], q[2];
   h q[3];
   c = measure q;

Iterative phase estimation
--------------------------

We can extend the two prior examples to iterative phase estimation. This
example makes use of gate modifiers and fast-feedback.

.. code:: c

   /*
    * Iterative phase estimation
    */
   OPENQASM 3;
   include "stdgates.inc";

   const n = 10;          // number of iterations
   const theta = 3 * pi / 8;  // phase angle on target qubit

   qubit q;    // phase estimation qubit
   qubit r;    // target qubit for the controlled-unitary gate
   angle[n] c; // phase estimation bits

   // initialize
   reset q;
   reset r;

   // prepare uniform superposition of eigenvectors of phase
   h r;

   // iterative phase estimation loop
   uint[n] power = 1;
   for i in [0: n - 1] {  // implicitly cast val to int
     reset q;
     h q;
     ctrl @ pow[power] @ phase(theta) q, r;
     inv @ phase(c) q;
     h q;
     measure q -> c[0];
     // newest measurement outcome is associated to a pi/2 phase shift
     // in the next iteration, so shift all bits of c left
     c <<= 1;
     power <<= 1;
   }

   // Now c contains the n-bit estimate of phi in the
   // eigenvalue e^{i*phi} and qreg r is projected to an
   // approximate eigenstate of the phase gate.

Ripple-carry adder
------------------

The ripple-carry adder :cite:`cuccaro04` shown in
Fig. `[fig:example:add] <#fig:example:add>`__ exhibits hierarchical use
of gate subroutines.

.. code:: c

   /*
    * quantum ripple-carry adder
    * Cuccaro et al, quant-ph/0410184
    */
   OPENQASM 3;
   include "stdgates.inc";

   gate majority a, b, c {
       cx c, b;
       cx c, a;
       ccx a, b, c;
   }

   gate unmaj a, b, c {
       ccx a, b, c;
       cx c, a;
       cx a, b;
   }

   qubit cin[1], a[4], b[4], cout[1];
   bit ans[5];
   uint[4] a_in = 1;  // a = 0001
   uint[4] b_in = 15; // b = 1111
   // initialize qubits
   reset cin;
   reset a;
   reset b;
   reset cout;

   // set input states
   for i in [0: 3] {
     if(bool(ain[i])) x a[i];
     if(bool(bin[i])) x b[i];
   }
   // add a to b, storing result in b
   majority cin[0], b[0], a[0];
   for i in [0: 2] { majority a[i], b[i + 1], a[i + 1]; }
   cx a[3], cout[0];
   for i in [2: -1: 0] { unmaj a[i],b[i+1],a[i+1]; }
   unmaj cin[0], b[0], a[0];
   measure b[0:3] -> ans[0:3];
   measure cout[0] -> ans[4];

Randomized benchmarking
-----------------------

A complete randomized benchmarking experiment could be described by a
high level program. After passing through the upper phases of
compilation, the program consists of many quantum circuits and
associated classical control. Benchmarking is a particularly simple
example because there is no data dependence between these quantum
circuits.

Each circuit is a sequence of random Clifford gates composed from a set
of basic gates (Fig. `[fig:example:rb] <#fig:example:rb>`__ uses the
gate set , , , and Paulis). If the gate set differs from the built-in
gate set, new gates can be defined using the statement. Each of the
randomly-chosen Clifford gates is separated from prior and future gates
by barrier instructions to prevent the sequence from simplifying to the
identity as a result of subsequent transformations.

.. code:: c

   // One randomized benchmarking sequence
   OPENQASM 3;
   include "stdgates.inc";

   qubit q[2];
   bit c[2];

   reset q;
   h q[0];
   barrier q;
   cz q[0], q[1];
   barrier q;
   s q[0];
   cz q[0], q[1];
   barrier q;
   s q[0];
   z q[0];
   h q[0];
   barrier q;
   measure q -> c;

Quantum process tomography
--------------------------

As in randomized benchmarking, a high-level program describes a quantum
process tomography (QPT) experiment. Each program compiles to
intermediate code with several independent quantum circuits that can
each be described using OpenQASM (version 2.0).
Fig. `[fig:example:qpt] <#fig:example:qpt>`__ shows QPT of a Hadamard
gate. Each circuit is identical except for the definitions of the and
gates. The empty definitions in the current example are placeholders
that define identity gates. For textbook QPT, the and gates are both
taken from the set :math:`\{I,H,SH\}` to prepare :math:`|0\rangle`,
:math:`|+\rangle`, and :math:`|+i\rangle` and measure in the :math:`Z`,
:math:`X`, and :math:`Y` basis.

.. code:: c

   OPENQASM 3;
   include "stdgates.inc";

   gate pre q { }   // pre-rotation
   gate post q { }  // post-rotation

   qubit q;
   bit c;
   reset q;
   pre q;
   barrier q;
   h q;
   barrier q;
   post q;
   c = measure q;

Basic quantum error-correction
------------------------------

This example of the 3-bit quantum repetition code
(Fig. `[fig:example:qec3] <#fig:example:qec3>`__) demonstrates how
OpenQASM (version 3.0) can express simple quantum error-correction
circuits.

.. code:: c

   // Repetition code syndrome measurement
   OPENQASM 3;
   include "stdgates.inc";

   qubit q[3];
   qubit a[2];
   bit c[3];
   bit syn[2];

   def syndrome qubit[3]:d, qubit[2]:a -> bit[2] {
     bit[2] b;
     cx d[0], a[0];
     cx d[1], a[0];
     cx d[1], a[1];
     cx d[2], a[1];
     measure a -> b;
     return b;
   }
   reset q;
   reset a;
   x q[0]; // insert an error
   barrier q;
   syn = syndrome q, a;
   // also valid: syndrome q, a -> syn;
   if(int(syn)==1) x q[0];
   if(int(syn)==2) x q[2];
   if(int(syn)==3) x q[1];
   c = measure q;

Surface code error-correction
-----------------------------

The surface code is one of the leading approaches to fault-tolerant
quantum computing. This example implements a fault-tolerant surface code
quantum memory with calls to kernel functions for logging and processing
the measurement data. These kernel functions must run concurrently with
quantum gates and may not have a deterministic running time (cite).

.. code:: c

   /*
    * Surface code quantum memory.
    *
    * Estimate the failure probability as a function
    * of parameters at the top of the file.
    */
   OPENQASM 3;
   include "stdgates.inc";

   const d = 3;         // code distance
   const m = 10;        // number of syndrome measurement cycles
   const shots = 1000;  // number of samples
   const n = d^2;       // number of code qubits

   uint[32] failures;  // number of observed failures

   kernel zfirst creg[n - 1], int, int;
   kernel send creg[n -1 ], int, int, int;
   kernel zlast creg[n], int, int -> bit;

   qubit data[n];  // code qubits
   qubit ancilla[n - 1];  // syndrome qubits
   /*
    * Ancilla are addressed in a (d-1) by (d-1) square array
    * followed by 4 length (d-1)/2 arrays for the top,
    * bottom, left, and right boundaries.
    */

   bit layer[n - 1];  // syndrome outcomes in a cycle
   bit data_outcomes[n];  // data outcomes at the end
   bit outcome;  // logical outcome

   /* Declare a sub-circuit for Hadamard gates on ancillas
    */
   def hadamard_layer qubit[n-1]:ancilla {
     // Hadamards in the bulk
     for row in [0: d-2] {
       for col in [0: d-2] {
         bit sum[32] = bit[32](row + col);
         if(sum[0] == 1)
           h ancilla[row * (d - 1) + col];
       }
     }
     // Hadamards on the left and right boundaries
     for i in [0: d - 2] {
       h ancilla[(d - 1)^2 + (d - 1) + i];
     }
   }

   /* Declare a sub-circuit for a syndrome cycle.
    */
   def cycle qubit[n]:data, qubit[n-1]:ancilla -> bit[n-1] {
     reset ancilla;
     hadamard_layer ancilla;

     // First round of CNOTs in the bulk
     for row in [0: d - 2] {
       for col in [0:d - 2] {
         bit sum[32] = bit[32](row + col);
         if(sum[0] == 0)
           cx data[row * d + col], ancilla[row * (d - 1) + col];
         if(sum[0] == 1) {
           cx ancilla[row * (d - 1) + col], data[row * d + col];
         }
       }
     }
     // First round of CNOTs on the bottom boundary
     for i in [0: (d - 3) / 2] {
       cx data[d * (d - 1) + 2 * i], ancilla[(d - 1) ^ 2 + ( d- 1) / 2 + i];
     }
     // First round of CNOTs on the right boundary
     for i in [0: (d - 3) / 2] {
       cx ancilla[(d - 1) ^ 2 + 3 * (d - 1) / 2 + i], data[2 * d - 1 + 2 * d * i];
     }
     // Remaining rounds of CNOTs, go here ...

     hadamard_layer ancilla;
     return measure ancilla;
   }

   // Loop over shots
   for shot in [1: shots] {

     // Initialize
     reset data;
     cycle data, ancilla -> layer;
     zfirst(layer, shot, d);

     // m cycles of syndrome measurement
     for i in [1: m] {
       cycle data, ancilla -> layer;
       send(layer, shot, i, d);
     }

     // Measure
     data_outcomes = measure data;

     outcome = zlast(data_outcomes, shot, d);
     failures += int(outcome);
   }

   /* The ratio of "failures" to "shots" is our result.
    * The data can be logged by the external functions too.
    */

Repeat-until-success circuits
-----------------------------

The while loop allows implementation of repeat-until-success circuits
that have a non-deterministic number of iterations but complete in a
very small number of iterations with high probability. This example from
:cite:`NC00` applies a Z-rotation by an irrational angle
using a discrete universal gate set.

.. code:: c

   /*
    * Repeat-until-success circuit for Rz(theta),
    * cos(theta-pi)=3/5, from Nielsen and Chuang, Chapter 4.
    */
   OPENQASM 3;
   include "stdgates.inc";

   /*
    * Applies identity if out is 01, 10, or 11 and a Z-rotation by
    * theta + pi where cos(theta)=3/5 if out is 00.
    * The 00 outcome occurs with probability 5/8.
    */
   def segment qubit[2]:anc, qubit:psi -> bit[2] {
     bit[2] b;
     reset anc;
     h anc;
     ccx anc[0], anc[1], psi;
     s psi;
     ccx anc[0], anc[1], psi;
     z psi;
     h anc;
     measure anc -> b;
     return b;
   }

   qubit input;
   qubit ancilla[2];
   bit flags[2] = "11";
   bit output;

   reset input;
   h input;

   // braces are optional in this case
   while(int(flags) != 0) {
     flags = segment ancilla, input;
   }
   rz(pi - arccos(3 / 5)) input;
   h input;
   output = measure input;  // should get zero

Relaxation characterization
---------------------------

Qubit relaxation is the rate at which a qubit goes from an excited state
towards the ground state. This is an exponential rate denoted as T1. The
experiment to characterize this requires a circuit with multiple simple
basic blocks, where each is a sequence of reset, excitation, delay and
measurement. The delays in this example are given in fixed intervals in
SI units. Here we do the tabulation via a kernel function. However,
there are other post-processing steps associated with this experiment,
namely fitting the T1 exponential decay curve. This happens in the
runtime environment of this experiment, and not on the controllers.

.. code:: c

   /* Measuring the relaxation time of a qubit
    * This example demonstrates the repeated use of fixed delays.
   */
   OPENQASM 3.0;
   include "stdgates.inc";

   length stride = 1us;            // time resolution of points taken
   const points = 50;              // number of points taken
   const shots = 1000;             // how many shots per point

   int[32] counts0, counts1 = 0;   // surviving |1> populations of qubits

   kernel tabulate(int[32]:counts, int[32]:shots, int[32]:num);

   cbit c0, c1;

   // define a gate calibration for an X gate on qubit 1
   defcal "openpulse" x %0 {
      play drive(%0), gaussian(100, 30, 5);
   }

   for p in [0 : points-1] {
       for i in [1 : shots] {
           // start of a basic block
           reset %0;
           reset %1;
           // excite qubits
           x %0;
           x %1;
           // wait for a fixed time indicated by loop counter
           delay[p * stride] %0;
           // wait for a fixed time indicated by loop counters
           delay[p * lengthof({x %1;})];
           // read out qubit states
           c0 = measure %0;
           c1 = measure %1;
           // increment counts memories, if a 1 is seen
           counts0 += int(c0);
           counts1 += int(c1);
       }
       // log survival probability curve
       tabulate(counts0, shots, p);
       tabulate(counts1, shots, p);
   }

Time alignment
--------------

Flexible alignment of gates can be achieved using stretch, even on
virtual qubits.

.. code:: c

   /* CPMG XY4 decoupling
    * This example demonstrates the use of stretch to
    * specify design intent on gate alignment, without
    * being tied to physical qubits and gates.
   */
   OPENQASM 3.0;
   include "stdgates.inc";

   stretch g;

   barrier q;
   cx q[0], q[1];
   delay[g] q[2];
   U q[2];
   delay[2*g] q[2];
   barrier q;

Dynamical decoupling
--------------------

Dynamical decoupling is a technique for mitigating decoherence by
alternating the direction of phase accumulation during a qubit’s idle
time. Timing has a high impact on the quality of the DD sequence. Here
we show an example of a CPMG-type DD where the rotations are about the X
and Y axis. The X and Y gates themselves have finite duration, and we
seek to time them such that their *centers* are equidistant in time. We
use negative lengths and stretch to accomplish this. This sequence is
defined on a generic qubit, not necessarily a physical one. Our use of
stretch makes the delays adjust as appropriate whenever a concrete qubit
is targetted.

.. code:: c

   /* CPMG XY4 decoupling
    * This example demonstrates the use of referential delays
    * and time alignment.
   */
   OPENQASM 3.0;
   include "stdgates.inc";

   length start_stretch = -0.5 * lengthof({x %0;}) + stretch
   length middle_stretch = -0.5 * lengthof({x %0;}) - 5 * lengthof({y %0;} + stretch
   length end_stretch = -0.5 * lengthof({y %0;}) + stretch

   box {
     delay[start_stretch] %0;
     x %0;
     delay[middle_stretch] %0;
     y %0;
     delay[middle_stretch] %0;
     x %0;
     delay[middle_stretch] %0;
     y %0;
     delay[end_stretch] %0;

     cx %2, %3;
     cx %1, %2;
     u %3;
   }

Pulse declarations
------------------

A notional example of a possible “openpulse” grammar for use within
blocks is shown below. The particular example is sufficient to describe
a typical implementation of with cross-resonance gates, where the
implementation consists of an echo sequence and a lower-level primitive.

.. code:: c

   defcalgrammar "openpulse";

   defcal x %0 {
      play drive(%0), gaussian(...);
   }

   defcal x %1 {
     play drive(%1), gaussian(...);
   }

   defcal rz(angle[20]:theta) %q {
     shift_phase drive(%q), -theta;
   }

   defcal measure %0 -> bit {
     complex[int[24]] iq;
     bit state;
     complex[int[12]] k0[1024] = [i0 + q0*j, i1 + q1*j, i2 + q2*j, ...];
     play measure(%0), flat_top_gaussian(...);
     iq = capture acquire(%0), 2048, kernel(k0);
     return threshold(iq, 1234);
   }

   defcal zx90_ix %0, %1 {
     play drive(%0, "cr1"), flat_top_gaussian(...);  // uses a non-default
                                                     // frame labeled "cr1"
   }

   defcal cx %0, %1 {
     zx90_ix %0, %1;
     x %0;
     shift_phase drive(%0, "cr1");
     zx90_ix %0, %1;
     x %0;
     x %1;
   }
