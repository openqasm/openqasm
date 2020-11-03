.. _sec:spec:

Language
========

Hereafter, OpenQASM refers to the extended language we now describe. The
human-readable form of OpenQASM is a simple C-like textual language.
Statements are separated by semicolons. Whitespace is ignored. The
language is case sensitive. Appendix `[app:summary] <#app:summary>`__
summarizes the language statements,
Appendix `[app:grammar] <#app:grammar>`__ specifies the grammar, and
Appendix `[app:semantics] <#app:semantics>`__ gives formal semantics.

Comments
--------

Comments begin with a pair of forward slashes and end with a new line:

.. code:: c

   // A comment line

A comment block begins with ``/*`` and ends with ``*/``:

.. code:: c

   /*
   A comment block
   */

Version string
--------------

The first (non-comment) line of an OpenQASM program may optionally be
indicating a major version M and minor version m. Version 3.0 is
described in this document. Multiple occurrences of the version keyword
are not permitted. The minor version number and decimal point are
optional. If they are not present, they are assumed to be zero.

Included files
--------------

The statement continues parsing as if the contents of the file were
inserted at the location of the statement.

.. code:: c

   // First non-comment is a version string
   OPENQASM 3.0;

   #include "stdgates.qasm";

   // Rest of QASM program

Types and Casting
-----------------

Generalities
~~~~~~~~~~~~

Variable identifiers must begin with a letter [A-Za-z], an underscore, a
percent sign, or an element from the Unicode character categories
Lu/Ll/Lt/Lm/Lo/NI :cite:`noauthorUnicodeNodate`.
Continuation characters may contain numbers. Variable identifiers may
not override a reserved identifier. All qubits are global variables.
When qubits are declared, their state is initially undefined. Qubits
cannot be declared within gates or subroutines. This simplifies OpenQASM
significantly since there is no need for quantum memory management.
However, it also means that users or compiler have to explicitly manage
the quantum memory. In addition to being assigned values within a
program, all of the classical types can be initialized on declaration.
Multiple comma-separated declarations can occur after the typename with
optional assignment on declaration for each. Any classical variable or
Boolean that is not explicitly initialized is undefined. Classical types
can be mutually cast to one another using the typename . We use the
notation to denote the width and precision of fixed point numbers, where
is the number of sign bits, is the number of integer bits, and is the
number of fractional bits. It is necessary to specify low-level
classical representations since OpenQASM operates at the intersection of
gates/analog control and digital feedback and we need to be able to
explicitly transform types to cross these boundaries. Classical types
are scoped to the braces within which they are declared.

Quantum types
~~~~~~~~~~~~~

Qubits
^^^^^^

There is a quantum bit () type that is interpreted as a reference to a
two-level subsystem of a quantum state. Quantum registers are static
arrays of qubits that cannot be dynamically resized. The statement
declares a reference to a quantum bit. The statement or declares a
quantum register with the given name identifier. The keyword is included
for backwards compatibility and will be removed in the future. Sizes
must always be constant positive integers. The label refers to a qubit
of this register, where
:math:`j\in \{0,1,\dots,\mathrm{size}(\mathrm{name})-1\}` is an integer.
Qubits are initially in an undefined state. A quantum operation is one
way to initialize qubit states.

Physical Qubits
^^^^^^^^^^^^^^^

While program qubits can be named, hardware qubits are referenced only
by integers with the syntax ``%``\ 0, %1, ..., %n. These qubit types are
used in lower parts of the compilation stack when emitting physical
circuits.

.. code:: c

   // Declare a qubit
   qubit gamma;
   // Declare a qubit with a Unicode name
   qubit γ;
   // Declare a qubit array with 20 qubits
   qubit qubit_array[20];
   // Declare usage of physical qubit 0
   qubit %0;

Classical types
~~~~~~~~~~~~~~~

Classical bits and registers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a classical bit type that takes values 0 or 1. Classical
registers are static arrays of bits. The classical registers model part
of the controller state that is exposed within the OpenQASM program. The
statement declares a classical bit, and or declares an array of bits
(register). The keyword is deprecated and will be removed in the future.
The label refers to a bit of this register, where :math:`j\in
\{0,1,\dots,\mathrm{size}(\mathrm{name})-1\}` is an integer. For
convenience, classical registers can be assigned a text string
containing zeros and ones of the same length as the size of the
register. It is interpreted to assign each bit of the register to
corresponding value 0 or 1 in the string, where the least-significant
bit is on the right.

.. code:: c

   // Declare an array of 20 bits
   bit bit_array[20]
   // Declare and assign an array of bits with decimal value of 15
   bit name[8] = "00001111";

Integers
^^^^^^^^

There are n-bit signed and unsigned integers. The statements and declare
signed 1:n-1:0 and unsigned 0:n:0 integers of the given size. The sizes
are always explicitly part of the type; there is no implicit width for
classical types in OpenQASM. Because register indices are integers, they
can be cast from classical registers containing measurement outcomes and
may only be known at run time. An n-bit classical register containing
bits can also be reinterpreted as an integer, and these types can be
mutually cast to one another using the type name, e.g. . As noted, this
conversion will be done assuming little-endian bit ordering.

.. code:: c

   // Declare a 32-bit unsigned integer
   uint[32] my_uint;
   // Declare a 32 bit signed integer
   int[32] my_int;

Signed fixed-point numbers
^^^^^^^^^^^^^^^^^^^^^^^^^^

There are fixed-point numbers with integer bits, fractional bits, and 1
sign bit. The statement declares a fixed-point number.

.. code:: c

   // Declare a 32-bit fixed point number.
   // The number is signed, has 7 integer bits
   // and 24 fractional bits.
   fixed[7, 24] my_fixed;

Floating point numbers
^^^^^^^^^^^^^^^^^^^^^^

IEEE 754 floating point registers may be declared with , where would
indicate a standard double-precision float. Note that some hardware
vendors may not support manipulating these values at run-time.

.. code:: c

   // Declare a single-precision 32-bit float
   float[32] my_float = π;

Fixed-point angles
^^^^^^^^^^^^^^^^^^

Fixed-point angles are interpreted as :math:`2\pi` times a 0:1:n-1
fixed-point number. This represents angles in the interval
:math:`[0,2\pi)` up to an error :math:`\epsilon\leq \pi/2^{n-1}` modulo
:math:`2\pi`. The statement declares an n-bit angle. OpenQASM3
introduces this specialized type because of the ubiquity of this angle
representation in phase estimation circuits and numerically controlled
oscillators found in hardware platform. Note that defining gate
parameters with types may be necessary for those parameters to be
compatible with run-time values on some platforms.

.. code:: c

   // Declare an angle with 20 bits of precision
   angle[20] my_angle;

Boolean types
^^^^^^^^^^^^^

There is a Boolean type that takes values or . Qubit measurement results
can be converted from a classical type to a Boolean using , where 1 will
be true and 0 will be false.

.. code:: c

   bit my_bit = 0;
   bool my_bool;
   // Assign a cast bit to a boolean
   my_bool = bool(my_bit);

Real constants
^^^^^^^^^^^^^^

To support mathematical expressions, there are immutable real constants
that are represented as double precision floating point numbers. On
declaration, they take their assigned value and cannot be redefined
within the same scope. These are constructed using an in-fix notation
and scientific calculator features such as scientific notation, real
arithmetic, logarithmic, trigonometric, and exponential functions
including , , , , , , and the built-in constant :math:`\pi`. The
statement defines a new constant. The expression on the right hand side
has a similar syntax as OpenQASM 2 parameter expressions; however,
previously defined constants can be referenced in later variable
declarations. Real constants are compile-time constants, allowing the
compiler to do constant folding and other such optimizations. Scientific
calculator-like operations on run-time values require kernel function
calls as described later and are not available by default. Real
constants can be cast to other types. Casting attempts to preserve the
semantics, but information can be lost, since variables have fixed
precision. Unlike casting from other types, implicit casts from real
constants are permitted.

A standard set of built-in constants which are included in the default
namespace are listed in table `1 <#tab:real-constants>`__.

.. code:: c

   // Declare a constant
   const my_const = 1234;
   // Scientific notation is supported
   const another_const = 1e2;
   // Constant expressions are supported
   const pi_by_2 = π / 2;
   // Constants may be cast to real-time values
   float[32] pi_by_2_val = float(pi_by_2)

.. container::
   :name: tab:real-constants

   .. table:: [tab:real-constants] Built-in real constants in OpenQASM3.

      +-------------------------------+--------------+--------------+---------------------+
      | Constant                      | Alphanumeric | Unicode      | Approximate Base 10 |
      +-------------------------------+--------------+--------------+---------------------+
      | (r)1-1(lr)2-2(rl)3-3(l)4-4 Pi | pi           | :math:`\pi`  | 3.1415926535...     |
      +-------------------------------+--------------+--------------+---------------------+
      | Tau                           | tau          | :math:`\tau` | 6.283185...         |
      +-------------------------------+--------------+--------------+---------------------+
      | Euler’s number                | euler_gamma  | :math:`e`    | 2.7182818284...     |
      +-------------------------------+--------------+--------------+---------------------+

Types related to timing
~~~~~~~~~~~~~~~~~~~~~~~

length
^^^^^^

We introduce a type and several keywords to express lengths of time.
Lengths are positive numbers with a unit of time. are used for SI time
units. is a backend-dependent unit equivalent to one waveform sample on
the backend. is an intrinsic function used to reference the duration of
another part of the program or the duration of a calibrated gate.

.. code:: c

   length one_second = 1000ms;
   length thousand_cycles = 1000dt;

stretch
^^^^^^^

We further introduce a type which is a sub-type of . Stretchable lengths
have variable non-negative length that is permitted to grow as necessary
to satisfy constraints. Stretch variables are resolved at compile time
into target-appropriate durations that satisfy a user’s specified design
intent. We distinguish different “orders" of stretch via types, where N
is an integer between 0 to 255. is an alias for the regular . At the
timing resolution stage of the compiler, higher order stretches will
suppress lower order stretches whenever they appear in the same scope on
the same qubits.

Aliasing
~~~~~~~~

The keyword allows quantum bits and registers to be referred to by
another name as long as the alias is in scope. For example, creates a
new reference to the last 4 qubits of the register . The qubit refers to
the qubit .

Register concatenation and slicing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two or more registers of the same type (i.e. classical or quantum) can
be concatenated to form a register of the same type whose size is the
sum of the sizes of the individual registers. The concatenated register
is a reference to the bits or qubits of the original registers. The
statement denotes the concatenation of registers and . A register cannot
be concatenated with any part of itself.

Classical and quantum registers can be indexed in a way that selects a
subset of (qu)bits, i.e. by an index set. A register so indexed is
interpreted as a register of the same type but with a different size.
The register slice is a reference to the original register. A register
cannot be indexed by an empty index set.

An index set can be specified by a single unsigned integer, a
comma-separated list of unsigned integers ``a,b,c,…``, or a range. A
range is written as or where , , and are integers (signed or unsigned).
The range corresponds to the set :math:`\{a, a+c, a+2c, \dots, a+mc\}`
where :math:`m` is the largest integer such that :math:`a+mc\leq b` if
:math:`c>0` and :math:`a+mc\geq b` if :math:`c<0`. If :math:`a=b` then
the range corresponds to :math:`\{a\}`. Otherwise, the range is the
empty set. If :math:`c` is not given, it is assumed to be one, and
:math:`c` cannot be zero. Note the index sets can be defined by
variables whose values may only be known at run time.

.. code:: c

   qubit[2] one;
   qubit[10] two;
   // Aliased register of twelve qubits
   let concatenated = one || two;
   // First qubit in aliased qubit array
   let first = concatenated[0];
   // Last qubit in aliased qubit array
   let last = concatenated[-1];
   // Qubits zero, three and five
   let qubit_selection = two[0, 3, 5];
   // First six qubits in aliased qubit array
   let sliced = concatenated[0:6];
   // Every second qubit
   let every_second = concatenated[0:2:12];

Gates
-----

In OpenQASM we refer to unitary quantum instructions as gates.

Built-in gates
~~~~~~~~~~~~~~

We define a mechanism for parameterizing unitary matrices to define new
quantum gates. The parameterization uses a built-in universal gate set
of single-qubit gates and a two-qubit entangling gate (CNOT)
:cite:`barenco95`. This basis is not an enforced compilation
target but a mechanism to define other gates. For many gates of
practical interest, there is a circuit representation with a polynomial
number of one- and two-qubit gates, giving a more compact representation
than requiring the programmer to express the full :math:`n \times n`
matrix. However, a general :math:`n`-qubit gate can be defined using an
exponential number of these gates.

We now describe this built-in gate set. There is one built-in two-qubit
gate

.. math::

   \mathrm{CX} := \left(\begin{array}{cccc}
   1 & 0 & 0 & 0 \\
   0 & 0 & 0 & 1 \\
   0 & 0 & 1 & 0 \\
   0 & 1 & 0 & 0 \end{array}\right)

called the controlled-NOT gate. The statement describes a CNOT gate that
flips the target qubit if and only if the control qubit is one. The
arguments cannot refer to the same qubit. If and are quantum registers
*with the same size*, the statement means apply for each index into
register . If instead, is a qubit and is a quantum register, the
statement means apply for each index into register . Finally, if is a
quantum register and is a qubit, the statement means apply for each
index into register .

.

All of the single-qubit unitary gates are also built-in and
parameterized as

.. math::

   U(\theta,\phi,\lambda) := R_z(\phi)R_y(\theta)R_z(\lambda) = \left(\begin{array}{cc}
       e^{-i(\phi+\lambda)/2}\cos(\theta/2) & -e^{-i(\phi-\lambda)/2}\sin(\theta/2) \\
   e^{i(\phi-\lambda)/2}\sin(\theta/2) & e^{i(\phi+\lambda)/2}\cos(\theta/2) \end{array}\right).

Here :math:`R_y(\theta)=\mathrm{exp}(-i\theta Y/2)` and
:math:`R_z(\phi)=\mathrm{exp}(-i\theta Z/2)`. When is a quantum
register, the statement means apply for each index into register . The
values :math:`\theta\in [0,2\pi)`, :math:`\phi\in [0,2\pi)`, and
:math:`\lambda\in
[0,2\pi)` in this base gate are angles whose precision is implementation
dependent [1]_. This specifies any element of :math:`SU(2)` up to a
global phase. For example, applies a Hadamard gate to qubit .

Finally, a built-in global phase gate allows the inclusion of arbitrary
global phase on circuits. adds a global phase of :math:`e^{i\gamma}` to
the circuit. e.g.:

.. _sec:macros:

Hierarchically defined unitary gates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For new gates, we associate them with a corresponding unitary
transformation by a sequence of built-in gates. For example, a CPHASE
operation is shown schematically in Fig. `[fig:gate] <#fig:gate>`__. The
corresponding OpenQASM code is

.. code:: c

   gate cphase(angle[32]: θ) a, b
   {
     U(0, 0, θ / 2) a;
     CX a, b;
     U(0, 0, -θ / 2) b;
     CX a, b;
     U(0, 0, θ / 2) b;
   }
   cphase(π / 2) q[0], q[1];

Note that this definition does not imply that must be implemented with
this series of gates. Rather, we have specified the unitary
transformation that corresponds to the symbol . The particular
implementation is up to the compiler, given information about the basis
gate set supported by a particular target.

In general, new gates are defined by statements of the form

.. code:: c

   // comment
   gate name(params) qargs
   {
     body
   }

where the optional parameter list is a comma-separated list of variable
parameters, and the argument list is a comma-separated list of qubit
arguments. The parameters are identifiers with angular types and default
to 32-bits. The qubit arguments are identifiers. If there are no
variable parameters, the parentheses are optional. At least one qubit
argument is required. The arguments in cannot be indexed within the body
of the gate definition.

.. code:: c

   // this is ok:
   gate g a
   {
     U(0, 0, 0) a;
   }
   // this is invalid:
   gate g a
   {
     U(0, 0, 0) a[0];
   }

Only built-in gate statements, calls to previously defined gates, and
timing directives can appear in . For example, it is not valid to
declare a classical register in a gate body. The statements in the body
can only refer to the symbols given in the parameter or argument list,
and these symbols are scoped only to the subroutine body. An empty body
corresponds to the identity gate. Gates must be declared before use and
cannot call themselves. The statement applies the gate, and the variable
parameters are given as angular types or in-place constant parameter
expressions which are cast to angles. The gate can be applied to any
combination of qubits and quantum registers *of the same size* as shown
in the following example. The quantum circuit given by

.. code:: c

   gate g qb0, qb1, qb2, qb3
   {
     // body
   }
   qubit qr0[1];
   qubit qr1[2];
   qubit qr2[3];
   qubit qr3[2];
   g qr0[0], qr1, qr2[0], qr3; // ok
   g qr0[0], qr2, qr1[0], qr3; // error!

has a second-to-last line that means

We provide this so that user-defined gates can be applied in parallel
like the built-in gates.

Quantum gate modifiers
~~~~~~~~~~~~~~~~~~~~~~

A gate modifier is a keyword that applies to a gate. A modifier
:math:`m` transforms a gate :math:`U` to a new gate :math:`m(U)` acting
on the same or larger Hilbert space. We include modifiers in OpenQASM
both for programming convenience and compiler analysis.

The modifier replaces its gate argument :math:`U` with its inverse
:math:`U^\dagger`. The inverse of any gate can be defined recursively by
reversing the order of the gates in its definition and replacing each of
those with their inverse. The base case is given by replacing with and
by .

The modifier replaces its gate argument :math:`U` by its :math:`k`\ th
power :math:`U^k` for some positive integer :math:`k` (not necessarily
constant). Such a gate can be trivially defined as :math:`k` repetitions
of the original gate, although more efficient implementations may be
possible.

The modifier replaces its gate argument :math:`U` by a
controlled-:math:`U` gate. The new control qubit is prepended to the
argument list for the controlled-:math:`U` gate. The modified gate does
not use any additional scratch space. A target may or may not be able to
execute the gate without further compilation.

.. code:: c

   // Define a controlled Rz operation using the ctrl gatemodifier.
   gate crz(angle[20]: θ) q1, q2 {
       ctrl @ U(θ, 0, 0) q1, q2;
   }

Built-in quantum instructions
-----------------------------

This sections describes built-in non-unitary operations.

Initialization
~~~~~~~~~~~~~~

The statement resets a qubit or quantum register to the state
:math:`|0\rangle`. This corresponds to a partial trace over those qubits
(i.e. discarding them) before replacing them with
:math:`|0\rangle\langle 0|`. Reset is shown in
Fig. `[fig:prepare] <#fig:prepare>`__.

.. code:: c

   // Initialize and reset an array of 10 qubits
   qubit[10] qubits;
   reset qubits;

Measurement
~~~~~~~~~~~

The statement measures the qubit(s) in the :math:`Z`-basis and assigns
the measurement outcome(s) to the target bit(s). For backwards
compatibility this is equivalent to which is also supported. Measurement
corresponds to a projection onto one of the eigenstates of :math:`Z`,
and qubit(s) are immediately available for further quantum computation.
Both arguments must be register-type, or both must be bit-type. If both
arguments are register-type and have the same size, the statement
broadcasts to for each index into register . Measurement is shown in
Fig. `[fig:measure] <#fig:measure>`__.

.. code:: c

   // Initialize, flip and measure an array of 10 qubits
   qubit[10] qubits;
   bit[10] bits;
   x qubits;
   bits = measure qubits;

Classical instructions
----------------------

We envision two levels of classical control that we call low-level
instructions and high-level kernel functions. Simple, fast instructions
control the flow of the program and allow basic computations on
lower-level parallel control processors. These instructions are likely
to have known durations and many such instructions might be executed
within the qubit coherence time. High-level kernel functions execute
arbitrary user-defined classical subroutines that may be neither fast
nor guaranteed to return. These assume a mechanism for passing data to
and from higher-level processors. The kernel functions run on the global
processor concurrently with operations on the local processors, if
possible. Kernel functions can write to the global controller’s memory,
which may not be directly accessible by the local controllers.

Low-level classical instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _generalities-1:

Generalities
^^^^^^^^^^^^

All types support the assignment operator . The left-hand-side (LHS) and
right-hand-side (RHS) of the assignment operator must be of the same
type. For real-time values assignment is by copy of the RHS value to the
assigned variable on the LHS.

.. code:: c

   int[32] a;
   int[32] b = 10; // Combined declaration and assignment

   a = b; // Assign b to a
   b = 0;
   a == b; // False
   a == 10; // True

.. _classical-bits-and-registers-1:

Classical bits and registers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Classical registers and bits support bitwise operators and the
corresponding assignment operators between registers of the same size:
and , or , xor . They support left shift and right shift by an unsigned
integer, and the corresponding assignment operators. The shift operators
shift bits off the end. They also support not ,  [2]_, and left and
right circular shift, and , respectively.

.. code:: c

   bit[8] a = "10001111";
   bit[8] b = "01110000";

   a << 1; // Bit shift left produces "00011110"
   rotl(a, 2) // Produces "00111110"
   a | b; // Produces "11111111"
   a & b; // Produces "00000000"

Comparison (Boolean) Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integers, fixed-point numbers, angles, bits, and classical registers can
be compared (:math:`>`, :math:`>=`, :math:`<`, :math:`<=`, :math:`==`,
:math:`!=`) and yield Boolean values. Boolean values support logical
operators: and , or , not . The keyword tests if an integer belongs to
an index set, for example returns if i equals 0 or 3 and otherwise.

.. code:: c

   bool a = false;
   int[32] b = 1;
   fixed[8, 12] c = 1.05;
   angle[32] d = pi;
   float[32] e = pi;

   a == false; // True
   a == bool(b); // False
   c >= b; // True
   d == pi; // True
   // Susceptible to floating point casting errors
   e == float(d);

.. _integers-1:

Integers
^^^^^^^^

Integer types support addition , subtraction , multiplication, and
division [3]_; the corresponding assignments , , , and ; as well as
increment and decrement .

.. code:: c

   int[32] a = 2;
   int[32] b = 3;

   a * b; // 5
   a += 4; // a == 6
   a /= b; // a == 2
   a++; // a == 3

Fixed-point numbers and angles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fixed-point and angle types support addition, subtraction,
multiplication, and division and the corresponding assignment operators.

.. code:: c

   angle[20] a = pi / 2;
   angle[20] b = pi;
   a + b; // 3/2 * pi
   angle[10] c;
   c = angle(a + b); // cast to angle[10]

Looping and branching
^^^^^^^^^^^^^^^^^^^^^

The statement branches to program if the Boolean evaluates to true and
may optionally be followed by .

.. code:: c

   bool target = false;
   qubit a;
   h a;
   bit output = measure qubit

   // example of branching
   if (target == output) {
      // do something
   } else {
      // do something else
   }

The statement loops over integer values in the indexset, assigning them
to . The for loop body is not permitted to modify the loop variable of
the indexset.

.. code:: c

   int[32] b;
   for i in {1, 5, 10} {
       b += i;
   } // b == 16

The statement executes program until the Boolean evaluates to
false [4]_. Variables in the loop condition statement may be modified
within the while loop body.

.. code:: c

   qubit q;
   bit result;

   int i = 0;
   // Keep applying hadamards and measuring a qubit
   // until 10, |1>s are measured
   while (i < 10) {
       h q;
       result = measure q;
       if (result) {
           i++;
       }
   }

A block can be exited with the statement . The statement can appear in
the body of a for or while loop. It returns control to the loop
condition. The statement terminates the program. In all of the
preceding, can also be replaced by a statement without the braces.

.. code:: c

   int[32] i = 0;

   while (i < 10) {
       i++;
       // continue to next loop iteration
       if (i == 2) {
           continue;
       }

       // some program

       // break out of loop
       if (i == 4) {
           break;
       }

       // more program
   }

Kernel function calls
~~~~~~~~~~~~~~~~~~~~~

Kernel functions are declared by giving their signature using the
statement where inputs is a comma-separated list of type names and
output is a single type name. They can be functions of any number of
arguments whose types correspond to the classical types of OpenQASM.
Inputs are passed by value. They can return zero or one value whose type
is any classical type in OpenQASM except real constants. If necessary,
multiple return values can be accommodated by concatenating registers.
The type and size of each argument must be known at compile time to
define data flow and enable scheduling. We do not address issues such as
how the kernel functions are defined and registered.

Kernel functions are invoked using the statement The functions are not
required to be idempotent. They may change the state of the process
providing the function. In our computational model, the kernel functions
are assumed to run concurrently with other classical and quantum
computations. The output of a kernel function can be assigned to a
variable on declaration using the assignment operator rather than the
arrow notation.

Subroutines
-----------

Subroutines are declared using the statement . Zero or more quantum bits
and registers are passed to the subroutine by reference or name in .
Classical types are passed by value in . The subroutines return up to
one classical type. All arguments are declared together with their type,
for example would define a quantum bit argument named . The output of a
subroutine can be assigned to a variable on declaration using the
assignment operator rather than the arrow notation.

Using subroutines, we can define an X-basis measurement with the program
. We can also define more general classes of single-qubit measurements
as . The type declarations are necessary if we want to mix qubit and
register arguments. For example, we might define a parity check
subroutine that takes qubits and registers

.. code:: c

   def xcheck qubit[4]:d, qubit:a -> bit {
     reset a;
     for i in [0: 3] cx d[i], a;
     return measure a;
   }

Naturally we can also use subroutines to define purely classical
operations, such as methods we can implement using low-level classical
instructions, like

.. code:: c

   const n = /* some size, known at compile time */;
   def parity(bit[n]:cin) -> bit {
     bit c;
     for i in [0: n - 1] {
       c ^= cin[i];
     }
     return c;
   }

We can make some measurements and call this subroutine on the results as
follows

.. code:: c

   c = measure q;
   c2 = measure r;
   result = parity(c || c2);

We require that we know the signature at compile time, as we do in this
example. We could also just as easily have used a kernel function for
this

.. code:: c

   const n = /* size of c + size of c2 */;
   kernel parity bit[n] -> bit;
   measure q -> c;
   measure r -> c2
   parity(c || c2) -> result;

Directives
----------

OpenQASM supports a directive mechanism that allows other information to
be included in the program. A directive begins with ``#pragma`` and
terminates at the end of the line. Directives can provide annotations
that give additional information to compiler passes and the target
system or simulator. Ideally the meaning of the program does not change
if some or all of the directives are ignored, so they can be interpreted
at the discretion of the consuming process.

Circuit timing
--------------

A key aspect of expressing code for quantum experiments is the ability
to control the timing of gates and pulses. Examples include
characterization of decoherence and crosstalk, dynamical decoupling,
dynamically corrected gates, and gate scheduling. This can be a
challenging task given the potential heterogeneity of calibrated gates
and their various durations. It is useful to specify gate timing and
parallelism in a way that is independent of the precise duration and
implementation of gates at the pulse-level description. In other words,
we want to provide the ability to capture *design intent* such as “space
these gates evenly to implement a higher-order echo decoupling sequence"
or “implement this gate as late as possible".

length and stretch types
~~~~~~~~~~~~~~~~~~~~~~~~

The type is used denote duration of time. Lengths are positive numbers
that are manipulated at compile time. Lengths have units which can be
any of the following:

-  SI units of time, such as

-  Backend-dependent unit, , equivalent to the duration of one waveform
   sample on the backend

It is often useful to reference the duration of other parts of the
circuit. For example, we may want to delay a gate for twice the duration
of a particular sub-circuit, without knowing the exact value to which
that duration will resolve. Alternatively, we may want to calibrate a
gate using some pulses, and use its duration as a new in order to delay
other parts of the circuit. The intrinsic function can be used for this
type of referential timing.

Below are some examples of values of type .

.. code:: c

       // fixed length, in standard units
       length a = 300ns;
       // fixed length, backend dependent
       length b = 800dt;
       // fixed length, referencing the duration of a calibrated gate
       length c = lengthof(defcal);
       // dynamic length, referencing a box within its context
       length d = lengthof(box);

We further introduce a type which is a sub-type of . Stretchable lengths
have variable non-negative length that is permitted to grow as necessary
to satisfy constraints. Stretch variables are resolved at compile time
into target-appropriate durations that satisfy a user’s specified design
intent.

Instructions whose duration is specified in this way become “stretchy",
meaning they can extend beyond their “natural length" to fill a span of
time. Stretchy s are the most obvious use case, but this can be extended
to other instructions too, e.g. rotating a spectator qubit while another
gate is in progress. Similarly, a whose definition contains stretchy
delays will be perceived as a stretchy gate by other parts of the
program.

For example, in order to ensure a sequence of gates between two barriers
will be left-aligned (Figure `[fig:alignment] <#fig:alignment>`__\ a),
whatever their actual durations may be, we can do the following:

.. code:: c

   	barrier q;
   	cx q[0], q[1];
   	u q[2];
   	cx q[3], q[4];
   	delay[stretchinf] q[0], q[1];
   	delay[stretchinf] q[2];
   	delay[stretchinf] q[3], q[4];
   	barrier q;

We can further control the exact alignment by giving relative weights to
the stretchy delays (Figure `[fig:alignment] <#fig:alignment>`__\ b):

.. code:: c

   	stretch g;
   	barrier q;
   	cx q[0], q[1];
   	delay[g];
   	u q[2];
   	delay[2*g];
   	barrier q;

[fig:leftalign]

[fig:leftalignresolved]

Lastly, we distinguish different “orders" of stretch via types, where N
is an integer between 0 to 255. is an alias for the regular . Higher
order stretches will suppress lower order stretches whenever they appear
in the same scope on the same qubits. A keyword is defined as an
infinitely stretchable length. It will always take precedence, and will
not changed if arithmetic operations are done on it. This is most useful
as a “don’t care" mechanism to specify delays that will just fill
whatever gap is present.

.. code:: c

       // stretchable length, with min=0 and max=inf
       stretch e;
       delay[e];
       // higher-order stretch which always mutes lower-order stretch
       stretch2 f;
       delay[2*f];
       // infinitely stretchable length, always anonymous.
       // other instruction don't care about the value to which this resolves.
       delay[stretchinf];

The concepts of and are inspired by the concept of “boxes and glues" in
the TeX language :cite:`knuth1984texbook`. This similarity
is natural; TeXaims to resolve the spacing between characters in order
to typeset a page, and the size of characters depend on the backend
font. In OpenQASM we intend to resolve the timing of different
instructions in order to meet high-level design intents, while the true
length of operations depend on the backend and compilation context.
There are however some key differences. Quantum operations can be
non-local, meaning the lengths set on one qubit can have side effects on
other qubits. The definition of -type variables and ability to define
multi-qubit stretches is intended to alleviate potential problems from
these side effects. Also contrary to TeX, we prohibit overlapping gates.

Operations on lengths
~~~~~~~~~~~~~~~~~~~~~

We can add two lengths, or multiply them by a constant, to get new
lengths. These are compile time operations since ultimately all lengths,
including stretches, will be resolved to constants.

.. code:: c

       length a = 300ns
       length b = lengthof({x %0})
       stretch c;
       // stretchy length with min=300ns
       length d = a + 2 * c
       // stretchy length with backtracking by up to half b
       length e = -0.5 * b + c

Delays (and other lengthed instructions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenQASM and OpenPulse have a instruction, whose duration is defined by
a . If the length passed to the delay contains stretch, it will become a
stretchy delay. We use square bracket notation to pass these length
parameters, to distinguish them from regular parameters (the compiler
will resolve these square-bracket parameters when resolving timing ).

Even though a instruction implements the identity channel in the ideal
case, it is intended to provide explicit timing. Therefore an explicit
instruction will prevent commutation of gates that would otherwise
commute. For example in
Figure `[fig:delaycommute] <#fig:delaycommute>`__\ a, there will be an
implicit delay between the ‘‘ gates on qubit 0. However, the ‘‘ gate is
still free to commute on that qubit, because the delay is implicit. Once
the delay becomes explicit (perhaps at lower stages of compilation),
gate commutation is prohibited
(Figure `[fig:delaycommute] <#fig:delaycommute>`__\ b).

Instructions other than delay can also have variable duration, if they
are explicitly defined as such. They can be called by passing a valid as
their duration. Consider for example a rotation called that is applied
for the entire duration of some other gate.

.. code:: c

       const amp = /* number */;
       stretch a;
       rotary(amp)[250ns] q;   // square brackets indicates duration
       rotary(amp)[a] q;       // a rotation that will stretch as needed

A multi-qubit instruction is *not* equivalent to multiple single-qubit
instructions. Instead a multi-qubit delay acts as a synchronization
point on the qubits, where the delay begins from the latest non-idle
time across all qubits, and ends simultaneously across all qubits. For
this reason, a instruction is exactly equivalent to a of a length zero
on the qubits involved.

.. code:: c

       cx q[0], q[1];
       cx q[2], q[3];
       // delay for 200 samples starting from the end of the longest cx
       delay[200dt] q[0:3];

A can be composed of positive or negative natural length, and of
positive stretch. After resolving the stretch, the instruction must end
up with non-negative duration.

For example, the code below inserts a dynamical decoupling sequence
where the \*centers\* of pulses are equidistant from each other. We
specify correct lengths for the delays by using backtracking operations
to properly take into account the finite length of each gate.

.. code:: c

   stretch s, t;
   length start_stretch = s - .5 * lengthof({x %0;})
   length middle_stretch = s - .5 * lengthof({x %0;}) - .5 * lengthof({y %0;}
   length end_stretch = s - .5 * lengthof({y %0;})

   delay[start_stretch] %0;
   x %0;
   delay[middle_stretch] %0;
   y %0;
   delay[middle_stretch] %0;=
   x %0;
   delay[middle_stretch] %0;
   y %0;
   delay[end_stretch] %0;

   cx %2, %3;
   delay[t] %1;
   cx %1, %2;
   u %3;

Boxed expressions
~~~~~~~~~~~~~~~~~

We introduce a expression for scoping a particular part of the circuit.
A boxed subcircuit can never be inlined (until target code generation
time), and optimizations across the boundary of a box are forbidden. The
contents inside the box can be optimized. The contents around the box
can be optimized too, e.g. it is permissible to commute a gate past a
box by knowing the unitary implemented by the box. Delays that are
within a box are implementation details of the box; they are invisible
to the outside scope and therefore do not prevent commutation.

We introduce a expression for labeling a box. We primarily use this to
later refer to the length of this box. Boxed expressions are good for
this because their contents are isolated and cannot be combined with
gates outside the box. Therefore, no matter how the contents of the box
get optimized, the has a well-defined meaning.

.. code:: c

       boxas mybox {
           cx q[0], q[1];
           delay[200ns] q[0];
       }
       delay[length(mybox)] q[2], q[3];
       cx q[2], q[3];

We introduce a expression. The contents of it will be boxed, and in
addition a total duration will be assigned to the box. This is useful
for conditionals where the box will declare a hard deadline. The natural
length of the box must be smaller than the declared boxto duration,
otherwise a compile-time error will be raised. The stretch inside the
box will always be set to fill the difference between the declared
length and the natural length.

.. code:: c

      // defines a 1ms box whose content is just a centered CNOT
       boxto 1ms {
           stretch a;
           delay[a] q;
           cx q[0], q[1];
           delay[a] q;
       }

Barrier instruction
~~~~~~~~~~~~~~~~~~~

The instruction of OpenQASM 2 prevents commutation and gate reordering
on a set of qubits across its source line. The syntax is and can be seen
in the following example

.. code:: c

   cx r[0], r[1];
   h q[0];
   h s[0];
   barrier r, q[0];
   h s[0];
   cx r[1], r[0];
   cx r[0], r[1];

This will prevent an attempt to combine the CNOT gates but will not
constrain the pair of gates, which might be executed before or after the
barrier, or cancelled by a compiler.

Pulse-level descriptions of gates and measurement
-------------------------------------------------

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
and measurement with user-selectable pulse grammar. A future document
will define a textualized representation of one such grammar, OpenPulse.
Here we restrict ourselves to defining the necessary interfaces within
OpenQASM to these pulse-level definitions of gates and measurement.

The entry point to such gate and measurement definitions is the keyword
analogous to the keyword, but where the body specifies a pulse-level
instruction sequence on *physical* qubits, e.g.

.. code:: c

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

.. code:: c

   defcal h %0 { ... }
   defcal h %1 { ... }

and so forth. Some operations require further specialization on
parameter values, so we also allow multiple declarations on the same
physical qubits with different parameter values, e.g.

.. code:: c

   defcal rx(pi) %0 { ... }
   defcal rx(pi / 2) %0 { ... }

Given multiple definitions of the same symbol, the compiler will match
the most specific definition found for a given operation. Thus, given,

#. ``defcal rx(angle[20]:theta) %q  ...``

#. ``defcal rx(angle[20]:theta) %0  ...``

#. ``defcal rx(pi / 2) %0  ...``

the operation ``rx(pi/2) %0`` would match to (3), ``rx(pi) %0`` would
match (2), ``rx(pi/2) %1`` would match (1).

Users specify the grammar used inside blocks with a declaration, or by
an optional grammar string in a definition, e.g.

.. code:: c

   defcalgrammar "openpulse";
   defcal "openpulse" measure %q -> bit { ... }

are two equivalent ways to specify that the definition uses the grammar.

Note that and communicate orthogonal information to the compiler. s
define unitary transformation rules to the compiler. The compiler may
freely invoke such rules on operations while preserving the structure of
a circuit as a collection of s and s. The declarations instead define
elements of a symbol lookup table. As soon as the compiler replaces a
with a definition, we have changed the fundamental structure of the
circuit. Most of the time symbols in the table will also have
corresponding definitions. However, if a userprovides a for a symbol
without a corresponding , then we treat such operations like the gates
of prior versions of OpenQASM.

.. [1]
   The intention is that the accuracy of these built-in gates is
   sufficient for the accuracy of the derived gates to not be limited by
   that of the built-in gates.

.. [2]
   computes the Hamming weight of the input register.

.. [3]
   If multiplication and division instructions are not available in
   hardware, they can be implemented by expanding into other
   instructions.

.. [4]
   This clearly allows users to write code that does not terminate. We
   do not discuss implementation details here, but one possibility is to
   compile into target code that imposes iteration limits
