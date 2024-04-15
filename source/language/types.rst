.. role:: raw-latex(raw)
   :format: latex
..

Types and Casting
=================

.. _identifiers:

Identifiers
-----------

Identifiers must begin with a letter [A-Za-z], an underscore or an element from
the Unicode character categories Lu/Ll/Lt/Lm/Lo/Nl :cite:`wikipediaUnicode`.
The set of permissible continuation characters consists of all members of the
aforementioned character sets with the addition of decimal numerals [0-9].
Identifiers may not override a reserved identifier.

.. _variables:

Variables
---------
Variables must be named according to the rules for identifiers (See :ref:`identifiers`).
Variables may be assigned values within a program. Variables representing any classical type
can be initialized on declaration. Any classical variable or Boolean that is not explicitly
initialized is undefined. Classical types can be mutually cast to one another using the typename.
See :ref:`castingSpecifics` for more details on casting.

Declaration and initialization must be done one variable at a time for both quantum and classical
types. Comma seperated declaration/initialization (``int x, y, z``) is NOT allowed for any type. For
example, to declare a set of qubits one must do

.. code-block::

   qubit q0;
   qubit q1;
   qubit q2;

and to declare a set of classical variables

.. code-block::

   int[32] a;
   float[32] b = 5.5;
   bit[3] c;
   bool my_bool = false;

We use the notation ``s:m:f`` to denote the width and precision of fixed point numbers,
where ``s`` is the number of sign bits, ``m`` is the number of integer bits, and ``f`` is the
number of fractional bits. It is necessary to specify low-level
classical representations since OpenQASM operates at the intersection of
gates/analog control and digital feedback and we need to be able to
explicitly transform types to cross these boundaries. Classical types
are scoped to the braces within which they are declared.

Quantum types
-------------

Qubits
~~~~~~

There is a quantum bit (``qubit``) type that is interpreted as a reference to a
two-level subsystem of a quantum state. The statement ``qubit name;``
declares a reference to a quantum bit. These qubits are referred
to as "virtual qubits" (in distinction to "physical qubits" on
actual hardware; see below). The statement ``qubit[size] name;``
declares a quantum register with ``size`` qubits.
Sizes must always be :ref:`compile-time constant <const-expression>` positive
integers.
Quantum registers are static arrays of qubits
that cannot be dynamically resized.

The label ``name[j]`` refers to a qubit of this register, where
:math:`j\in \{0,1,\dots,\mathrm{size}(\mathrm{name})-1\}` is an integer.

.. note::

   To be compliant with the base OpenQASM 3.0 specification, an implementation
   is only required to allow this "quantum-register indexing" with a
   :ref:`compile-time constant value <const-expression>` (those with ``const``
   types).  Implementations are permitted to treat indexing into a quantum
   register with a value of non-\ ``const`` type as an error.  Consult your
   compiler and hardware documentation for details.

.. code-block::

   // Valid statements

   include "stdgates.inc";

   qubit[5] q1;
   const uint SIZE = 4;
   uint runtime_u = 2;
   qubit[SIZE] q2;  // Declare a 4-qubit register.

   x q1[0];
   z q2[SIZE - 2];  // The index operand is of type `const uint`.


   // Validity is implementation-defined.

   x q1[runtime_u];
   // Indexing with a value with a non-`const` type (`uint`, in this case) is
   // not guaranteed to be supported.


The keyword ``qreg`` is included
for backwards compatibility and will be removed in the future.

Qubits are initially in an undefined state. A quantum ``reset`` operation is one
way to initialize qubit states.

All qubits are global variables.
Qubits cannot be declared within gates or subroutines. This simplifies OpenQASM
significantly since there is no need for quantum memory management.
However, it also means that users or compiler have to explicitly manage
the quantum memory.

.. code-block::

   // Declare a qubit
   qubit gamma;
   // Declare a qubit with a Unicode name
   qubit γ;
   // Declare a qubit register with 20 qubits
   qubit[20] qubit_array;

.. _physical-qubits:

Physical Qubits
~~~~~~~~~~~~~~~

Physical qubits refer to particular hardware qubits. Therefore, they are only fully defined with
respect to a target device that has a published device topology. The hardware provider determines
the integer-labels associated with each qubit within the device's topology.

While virtual qubits can be named, hardware qubits are referenced by the syntax ``$[NUM]``, where
``NUM`` is a non-negative integer. Any integer included in the published device topology is a valid
physical qubit identifier. Note that this implies that physical qubit identifier indices may be
non-consecutive, depending on the device.

Like virtual qubits, physical qubits are global variables, but unlike virtual qubits, they must
not be declared.

Qubit parameters in a ``defcal`` declaration must be physical qubits. Calibrations are valid only
for a particular set of physical qubits. See also :ref:`pulse gates <pulse-gates>`.

Physical qubits cannot be used in ``gate`` statements. See also
:ref:`gate definitions <gate-statement>`.

Physical qubits are also used in lower parts of the compilation stack when emitting physical
circuits. A physical circuit is one which only references physical qubits, and every operation
used in the circuit has an associated ``defcal``, which we refer to as hardware-native gates and
measurements.

.. code-block::

   // CNOT gate between physical qubits 0 and 1
   CX $0, $1;
   // Define the pulse-level instruction sequence for ``h`` on physical qubit 0
   defcal h $0 { ... }

Physical qubit constraints
..........................

Physical qubits, by definition, reference particular hardware qubits. Circuit equivalence does not
hold over permutations of physical qubit labels. Thus, physical qubits cannot be remapped by a
compiler or hardware provider without opt-in from the programmer.

Note that while physical circuits require physical qubits, the converse need not be true. A circuit
that would require routing or gate decomposition to run (i.e., does not have a ``defcal`` for every
operation in the circuit) would by definition not be a physical circuit. However, physical qubits
can still be used in such circuits.

For example, a program defines the ``H`` gate with the ``gate`` statement, without a corresponding
``defcal`` of ``H``. ``H`` is therefore a supported gate, but not a hardware-native gate. The
compiler can decompose the statement ``H $0;`` to hardware-native gates, while still respecting
strict qubit mapping.

It is possible to write a partially-constrained program with both physical and virtual qubits.
Such programs are also non-physical circuits, and may or may not be supported by compilers or
hardware providers.


Classical scalar types
----------------------

Classical bits and registers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a classical bit type that takes values 0 or 1. Classical
registers are static arrays of bits. The classical registers model part
of the controller state that is exposed within the OpenQASM program. The
statement ``bit name;`` declares a classical bit, and or ``bit[size] name;`` declares a register of
``size`` bits. The label ``name[j]`` refers to a bit of this register, where :math:`j\in
\{0,1,\dots,\mathrm{size}(\mathrm{name})-1\}` is an integer.

Bit registers may also be declared as ``creg name[size]``. This is included for backwards
compatibility and may be removed in the future.

For convenience, classical registers can be assigned a text string
containing zeros and ones of the same length as the size of the
register. It is interpreted to assign each bit of the register to
corresponding value 0 or 1 in the string, where the least-significant
bit is on the right.

.. code-block::

   // Declare a register of 20 bits
   bit[20] bit_array;
   // Declare and assign a register of bits with decimal value of 15
   bit[8] name = "00001111";

Integers
~~~~~~~~

There are n-bit signed and unsigned integers. The statements ``int[size] name;`` and ``uint[size] name;`` declare
signed 1:n-1:0 and unsigned 0:n:0 integers of the given size. The sizes
and the surrounding brackets can be omitted (*e.g.* ``int name;``) to use
a precision that is specified by the particular target architecture.
Bit-level operations cannot be used on types without a specified width, and
unspecified-width types are different to *all* specified-width types for
the purposes of casting.
Because register indices are integers, they
can be cast from classical registers containing measurement outcomes and
may only be known at run time. An n-bit classical register containing
bits can also be reinterpreted as an integer, and these types can be
mutually cast to one another using the type name, e.g. ``int[16](c)``. As noted, this
conversion will be done assuming little-endian bit ordering. The example
below demonstrates how to declare, assign and cast integer types amongst
one another.

.. code-block::

   // Declare a 32-bit unsigned integer
   uint[32] my_uint = 10;
   // Declare a 16 bit signed integer
   int[16] my_int;
   my_int = int[16](my_uint);
   // Declare a machine-sized integer
   int my_machine_int;

Floating point numbers
~~~~~~~~~~~~~~~~~~~~~~

IEEE 754 floating point registers may be declared with ``float[size] name;``, where ``float[64]`` would
indicate a standard double-precision float. Note that some hardware
vendors may not support manipulating these values at run-time.

Similar to integers, floating-point registers can be declared with an
unspecified size.  The resulting precision is then set by the particular target
architecture, and the unspecified-width type is different to all specified-width
types for the purposes of casting.

.. code-block::

   // Declare a single-precision 32-bit float
   float[32] my_float = π;
   // Declare a machine-precision float.
   float my_machine_float = 2.3;

.. _void-type:

Void type
~~~~~~~~~

Subroutines and externs that do not return a value implicitly return ``void``.
The ``void`` type is unrealizable and uninstantiable, and thus cannot be
attached to an identifier or used as a cast operator. The keyword ``void`` is
reserved for potential future use.

.. _angle-type:

Angles
~~~~~~

OpenQASM 3 includes a new type to represent classical angles: ``angle``.
This type is intended to make manipulations of angles more efficient at runtime,
when the hardware executing the program does not have built-in support for
floating-point operations.  The manipulations on ``angle`` values are designed
to be significantly less expensive when done using integer hardware than the
equivalent software emulation of floating-point operations, by using the
equivalence of angles modulo :math:`2\pi` to remove the need for large dynamic
range.

In brief, the type ``angle[size]`` is manipulated very similarly to a single
unsigned integer, where the value ``1`` represents an angle of
:math:`2\pi/2^{\text{size}}`, and the largest representable value is
this subtracted from :math:`2\pi`.  Addition with other angles, and
multiplication and division by unsigned integers is defined by standard
unsigned-integer arithmetic, with more details found in :ref:`the section on
classical instructions <classical-instructions>`.

The statement ``angle[size] name;`` statement declares a new angle called
``name`` with ``size`` bits in its representation.  Angles can be assigned
values using the constant ``π`` or ``pi``, such as::

   // Declare a 20-bit angle with the value of "π/2"
   angle[20] my_angle = π / 2;
   // Declare a machine-sized angle
   angle my_machine_angle;

The bit representation of the type ``angle[size]`` is such that if
``angle_as_uint`` is the integer whose representation as a ``uint[size]`` has
the same bit pattern, the value of the angle (using exact mathematical
operations on the field of real numbers) would be

.. math::

   2\pi \times \frac{\text{angle_as_uint}}{2^{\text{size}}}

This "mathematical" value is the value used in casts from floating-point values
(if available), whereas casts to and from ``bit[size]`` types reinterpret the
bits directly.  This means that, unless ``a`` is sufficiently small::

  float[32] a;
  angle[32](bit[32](uint[32](a))) != angle[32](a)

Explicitly, the most significant bit (bit index ``size - 1``) correpsonds to
:math:`\pi`, and the least significant bit (bit index ``0``) corresponds to
:math:`2^{-\text{size} + 1}\pi`.  For example, with the most-significant bit on
the left in the bitstrings::

   angle[4] my_pi = π;  // "1000"
   angle[6] my_pi_over_two = π/2;  // "010000"
   angle[8] my_angle = 7 * (π / 8);  // "01110000"

Angles outside the interval :math:`[0, 2\pi)` are represented by their values
modulo :math:`2\pi`.  Up to this modulo operation, the closest ``angle[size]``
representation of an exact mathematical value is different from the true value
by at most :math:`\epsilon\leq \pi/2^{\text{size}}`.


Complex numbers
~~~~~~~~~~~~~~~

Complex numbers may be declared as ``complex[float[size]] name``, where ``size``
is the size of the IEEE-754 floating-point number used to store the real and
imaginary components.  Each component behaves as a ``float[size]`` type.  The
designator ``[size]`` can be omitted to use the default hardware ``float``, and
``complex`` with no arguments is a synonym for ``complex[float]``.

Imaginary literals are written as a decimal-integer or floating-point literal
followed by the letters ``im``.  There may be zero or more spaces or tabs
between the numeric component and the ``im`` component.  The type of this token
is ``complex`` (its value has zero real component), and the component type is as
normal given the floating-point literal, or the machine-size ``float`` if the
numeric component is an integer.

The real and imaginary components of a complex number can be extracted using the
builtin functions ``real()`` and ``imag()`` respectively.  The output types of
these functions is the component type specified in the type declaration.  For
example, given a declaration ``complex[float[64]] c;`` the output type of
``imag(c)`` would be ``float[64]``.  The ``real()`` and ``imag()`` functions
can be used in compile-time constant expressions when called on compile-time
constant values.

.. code-block::

   complex[float[64]] c;
   c = 2.5 + 3.5im;
   complex[float] d = 2.0+sin(π/2) + (3.1 * 5.5 im);
   float d_real = real(d);  // equal to 3.0

.. note::

   Real-world hardware may not support run-time manipulation of ``complex``
   values.  Consult your hardware's documentation to determine whether these
   language features will be available at run time.

.. warning::

   The OpenQASM 3.0 specification only directly permits complex numbers with
   floating-point component types.  Individually language implementations may
   choose to make other component types available, but this version of the
   specification prescribes no portable semantics in these cases.  It is
   possible that a later version of the OpenQASM specification will define
   semantics for non-\ ``float`` component types.

Boolean types
~~~~~~~~~~~~~

There is a Boolean type ``bool name;`` that takes values ``true`` or ``false``. Qubit measurement results
can be converted from a classical ``bit`` type to a Boolean using ``bool(c)``, where 1 will
be true and 0 will be false.

.. code-block::

   bit my_bit = 0;
   bool my_bool;
   // Assign a cast bit to a boolean
   my_bool = bool(my_bit);


.. _const-expression:

Compile-time constants
----------------------

A typed declaration of a scalar type may be modified by the ``const`` keyword,
such as ``const int a = 1;``.  This defines a compile-time constant.  Values of
type ``const T`` may be used in all locations where a value of type ``T`` is
valid.  ``const``-typed values are required when specifying the widths of types
(e.g. in ``float[SIZE] f;``, ``SIZE`` must have a ``const`` unsigned integer
type).  All scalar literals are ``const`` types.

.. code-block::

   // Valid statements
   
   const uint SIZE = 32;  // Declares a compile-time unsigned integer.

   qubit[SIZE] q1;  // Declares a 32-qubit register called `q1`. 
   int[SIZE] i1;    // Declares a signed integer called `i1` with 32 bits.


   // Invalid statements

   uint runtime_size = 32;
   qubit[runtime_size] q2;  // Invalid; runtime_size is not a `const` type.
   int[runtime_size] i2;    // Invalid for the same reason.

.. _const-expression-initialization:

Identifiers whose type is ``const T`` must be initialized, and may not be
assigned to in subsequent statements.  The type of the result of the
initialization expression for a ``const`` declaration must be ``const S``, where
``S`` is a type that is either ``T`` or can be :ref:`implicitly promoted
<implicit-promotion-rules>` to ``T``.

.. code-block::

   // Valid statements

   const uint u1 = 4;
   const int[8] i1 = 8;
   float[64] runtime_f1 = 2.0;

   const uint u2 = u1;       // `u1` is of type `const uint`.
   const float[32] f2 = u1;  // `const uint` is implicitly promoted to `const float[32]`.


   // Invalid statements

   const int[64] i2 = f2;  // `const float[32]` cannot be implicitly promoted to `const int[64]`.
   const float[64] f3 = runtime_f1;  // `runtime_f1` is not `const`.


.. _const-expression-operator:

Operator expressions, e.g. ``a + b`` (addition), ``a[b]`` (bit-level indexing)
and ``a == b`` (equality), and :ref:`certain built-in functions
<const-expression-functions>` acting only on ``const`` operands will be
evaluated at compile time.  The resulting values are of type ``const T``, where
the type ``T`` is the type of the result when acting on non-\ ``const``
operands.

.. code-block::

   // Valid statements

   const uint[8] SIZE = 5;

   const uint[16] u1 = 2 * SIZE;  // Compile-time value 10.
   const float[64] f1 = 5.0 * SIZE;  // Compile-time value 25.0.
   const bit b1 = u1[1];  // Compile-time value `"1"`.
   const bit[SIZE - 1] b2 = u1[0:3];  // Compile-time value `"1010"`.


.. _const-expression-cast:

The resultant type of a cast to type ``T`` is ``const T`` if the input value has
a type ``const S``, where values of type ``S`` can be cast to type ``T``.  If
``S`` cannot be cast to ``T``, the expression is invalid.  The cast operator
does not contain the keyword ``const``.

.. code-block::

   // Valid statements

   const float[64] f1 = 2.5;
   uint[8] runtime_u = 7;

   const int[8] i1 = int[8](f1);  // `i1` has compile-time value 2.
   const uint u1 = 2 * uint(f1);  // `u1` has compile-time value 4.


   // Invalid statements

   const bit[2] b1 = bit[2](f1);  // `float[64]` cannot be cast to `bit[2]`.
   const int[16] i2 = int[16](runtime_u);  // Casting runtime values is not `const`.


.. _const-expression-nonconst:

The resultant type of any expression involving a value that is not ``const`` is
not ``const``.  The output type of a call to a subroutine defined by a ``def``,
or a call to a subroutine linked by an ``extern`` statement is not ``const``.
In these cases, values of type ``const T`` are converted to type ``T`` (which
has no runtime cost and no effect on the value), then evaluation continues as
usual.

.. code-block::

   // Valid statements

   int[8] runtime_i1 = 4;

   def f(int[8] a) -> int[8] {
      return a;
   }


   // Invalid statements

   const int[8] i2 = 2 * runtime_i1;
   // Initialization expression has type `int[8]`, not `const int[8]`.
   const int[8] i3 = f(runtime_i1);
   // User-defined function calls do not propagate `const` values.


Built-in constants
~~~~~~~~~~~~~~~~~~

Six identifiers are automatically defined in the global scope at the beginning
of all OpenQASM 3 programs.  There are two identifiers for each of the
mathematical constants :math:`\pi`, :math:`\tau = 2\pi` and Euler's number
:math:`e`.  Each of these values has one ASCII-only identifier and one
single-Unicode-character identifier.

.. container::
   :name: tab:real-constants

   .. table:: [tab:real-constants] Built-in real constants in OpenQASM3 of type ``float[64]``.

      +-------------------------------+--------+--------------+---------------------+
      | Constant                      | ASCII  | Unicode      | Approximate Base 10 |
      +===============================+========+==============+=====================+
      | :math:`\pi`                   | pi     | π            | 3.1415926535...     |
      +-------------------------------+--------+--------------+---------------------+
      | :math:`\tau = 2\pi`           | tau    | τ            | 6.283185...         |
      +-------------------------------+--------+--------------+---------------------+
      | Euler’s number :math:`e`      | euler  | ℇ            | 2.7182818284...     |
      +-------------------------------+--------+--------------+---------------------+


.. _const-expression-functions:

Built-in constant expression functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following identifiers are compile-time functions that take ``const`` inputs
and have a ``const`` output.  The normal implicit casting rules apply to the
inputs of these functions.

.. note::

   These functions may not be available for use on runtime values; consult your
   compiler and hardware documentation for details.

.. container::
   :name: tab:built-in-math

   .. table:: Built-in mathematical functions in OpenQASM3.

      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | Function | Input Range/Type, [...]             | Output Range/Type                    | Notes                                  |
      +==========+=====================================+======================================+========================================+
      | arccos   | ``float`` on :math:`[-1, 1]`        | ``float`` on :math:`[0, \pi]`        | Inverse cosine.                        |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | arcsin   | ``float`` on :math:`[-1, 1]`        | ``float`` on :math:`[-\pi/2, \pi/2]` | Inverse sine.                          |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | arctan   | ``float``                           | ``float`` on :math:`[-\pi/2, \pi/2]` | Inverse tangent.                       |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | ceiling  | ``float``                           | ``float``                            | Round to the nearest representable     |
      |          |                                     |                                      | integer equal or greater in value.     |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | cos      | (``float`` or ``angle``)            | ``float``                            | Cosine.                                |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | exp      | ``float``                           | ``float``                            | Exponential :math:`e^x`.               |
      |          |                                     |                                      |                                        |
      |          | ``complex``                         | ``complex``                          |                                        |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | floor    | ``float``                           | ``float``                            | Round to the nearest representable     |
      |          |                                     |                                      | integer equal or lesser in value.      |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | log      | ``float``                           | ``float``                            | Logarithm base :math:`e`.              |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | mod      | ``int``, ``int``                    | ``int``                              | Modulus.  The remainder from the       |
      |          |                                     |                                      | integer division of the first argument |
      |          | ``float``, ``float``                | ``float``                            | by the second argument.                |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | popcount | ``bit[_]``                          | ``uint``                             | Number of set (1) bits.                |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | pow      | ``int``, ``uint``                   | ``int``                              | :math:`\texttt{pow(a, b)} = a^b`.      |
      |          |                                     |                                      |                                        |
      |          | ``float``, ``float``                | ``float``                            | For floating-point and complex values, |
      |          |                                     |                                      | the principal value is returned.       |
      |          | ``complex``, ``complex``            | ``complex``                          |                                        |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | rotl     | ``bit[n] value``, ``int distance``  | ``bit[n]``                           | Rotate the bits in the representation  |
      |          |                                     |                                      | of ``value`` by ``distance`` places    |
      |          | ``uint[n] value``, ``int distance`` | ``uint[n]``                          | to the left (towards higher            |
      |          |                                     |                                      | indices).  This is similar to a bit    |
      |          |                                     |                                      | shift operation, except the vacated    |
      |          |                                     |                                      | bits are filled from the overflow,     |
      |          |                                     |                                      | rather than being set to zero.  The    |
      |          |                                     |                                      | width of the output is set equal to    |
      |          |                                     |                                      | the width of the input.                |
      |          |                                     |                                      |                                        |
      |          |                                     |                                      | ``rotl(a, n) == rotr(a, -n)``.         |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | rotr     | ``bit[n] value``, ``int distance``  | ``bit[n]``                           | Rotate the bits in the representation  |
      |          |                                     |                                      | of ``value`` by ``distance`` places to |
      |          | ``uint[n] value``, ``int distance`` | ``uint[n]``                          | the right (towards lower indices).     |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | sin      | (``float`` or ``angle``)            | ``float``                            | Sine.                                  |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | sqrt     | ``float``                           | ``float``                            | Square root.  This always returns the  |
      |          |                                     |                                      | principal root.                        |
      |          | ``complex``                         | ``complex``                          |                                        |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+
      | tan      | (``float`` or ``angle``)            | ``float``                            | Tangent.                               |
      +----------+-------------------------------------+--------------------------------------+----------------------------------------+

For each built-in function, the chosen overload is the first one to appear in
the list above where all given operands can be implicitly cast to the valid
input types.  The output type is not considered when choosing an overload.  It
is an error if there is no valid overload for a given sequence of operands.

.. code-block::

   // Valid statements.

   const float[64] f1 = 2.5;
   const int[8] i1 = 4;
   const uint[4] u1 = 3;
   const bit[8] b1 = "0010_1010";
   const complex[float[64]] c1 = 1.0 + 2.0im;

   const float[64] f2 = 2.0 * exp(f1);
   const float[64] f3 = exp(i1);
   // The ``float -> float`` overload of ``exp`` is chosen in both of these
   // cases; in the first, there is an exact type match, in the second the
   // ``int[8]`` input can be implicitly promoted to ``float``.

   const int[8] i2 = pow(i1, u1);
   // Value 64, expression has type `const int`.  The first overload of `pow`
   // is chosen, because `i1` can be implicitly promoted to `const int` and
   // `u1` to `const uint`.

   const float[64] f4 = pow(i1, -2);
   // Value 0.0625, expression has type `const float`.  The second,
   // `(float, float) -> float`, overload is chosen, because `-2` (type
   // `const int`) cannot be implicitly promoted to `const uint`, but both
   // input types can be implicitly promoted to `float`.  The `complex` overload
   // is not attempted, because it has lower priority.

   const bit[8] b2 = rotl(b1, 3);
   // Value "0101_0001", expression has type `const bit[8]`.


   // Invalid statements.

   const complex[float[64]] c2 = mod(c1, 2);
   // No valid overload is possible; the first given operand has type
   // `const complex[float[64]]`, which cannot be implicitly promoted to
   // `int` or `float`.


Literals
--------

There are five types of literals in OpenQASM 3, integer, float, boolean,
bit string, and timing.  These literals have ``const`` types.

Integer literals can be written in decimal without a prefix, or as a hex, octal, or
binary number, as denoted by a leading ``0x/0X``, ``0o``, or ``0b/0B`` prefix.
Non-consecutive underscores ``_`` may be inserted between the first and last
digit of the literal to improve readability for large values.

.. code-block::

   int i1 = 1; // decimal
   int i2 = 0xff; // hex
   int i3 = 0xffff_ffff // hex with _ for readability
   int i4 = 0XBEEF; // uppercase HEX
   int i5 = 0o73; // octal
   int i6 = 0b1101; // binary
   int i7 = 0B0110_1001; // uppercase B binary with _ for readability
   int i8 = 1_000_000 // 1 million with _ for readability

Float literals contain either
   - one or more digits followed by a ``.`` and zero or more digits,
   - a ``.`` followed by one or more digits.

In addition, scientific notation can be used with a signed or unsigned integer
exponent.

.. code-block::

   float f1 = 1.0;
   float f2 = .1; // leading dot
   float f3 = 0.; // trailing dot
   float f4 = 2e10; // scientific
   float f5 = 2e+1; // scientific with positive signed exponent
   float f6 = 2.0E-1; // uppercase scientific with signed exponent

The two boolean literals are ``true`` and ``false``.

Bit string literals are denoted by double quotes ``"`` surrounding a number of
zero and one digits, and may include non-consecutive underscores to improve
readability for large strings.

.. code-block::

   bit[8] b1 = "00010001";
   bit[8] b2 = "0001_0001"; // underscore for readability

Timing literals are float or integer literals with a unit of time.
``ns, μs, us, ms, and s`` are used for SI time units. ``dt`` is a
backend-dependent unit equivalent to one waveform sample.

.. code-block::

   duration one_second = 1000ms;
   duration thousand_cycles = 1000dt;

.. _types-arrays:

Arrays
------

Statically-sized arrays of values can be created and initialized, and individual elements
can be accessed, using the following general syntax:

.. code-block::

   array[int[32], 5] myArray = {0, 1, 2, 3, 4};
   array[float[32], 3, 2] multiDim = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};

   int[32] firstElem = myArray[0]; // 0
   int[32] lastElem = myArray[4]; // 4
   int[32] alsoLastElem = myArray[-1]; // 4
   float[32] firstLastElem = multiDim[0, 1]; // 1.2
   float[32] lastLastElem = multiDim[2, 1]; // 3.2
   float[32] alsoLastLastElem = multiDim[-1, -1]; // 3.2

   myArray[4] = 10; // myArray == {0, 1, 2, 3, 10}
   multiDim[0, 0] = 0.0; // multiDim == {{0.0, 1.2}, {2.1, 2.2}, {3.1, 3.2}}
   multiDim[-1, 1] = 0.0; // multiDim == {{0.0, 1.2}, {2.1, 2.2}, {3.1, 0.0}}

The first argument to the ``array`` declaration is the base type
of the array. The supported classical types include various sizes of ``bit``,
``int``, ``uint``, ``float``, ``complex``, and ``angle``, as well as
``bool`` and ``duration``. Note that ``stretch`` is not a valid array
base type.

Arrays cannot be resized or reshaped. Arrays are statically typed, and cannot
implicitly convert to or from any other type.

The size of an array is constant and immutable, and is recorded once, at
declaration time.

Array declarations allocate memory of suitable size and alignment to
accommodate the storage of its elements.

If the array declaration is direct-initialized via initializer list, its elements
are initialized to the values provided by the initializer list.  Otherwise, the
memory allocated is not initialized, and that memory's content is undefined.

Arrays may be passed as parameters or arguments to functions.

When an array, or slice of an array, is passed as argument to a function, the behavior accords to that described in :any:`arrays-in-subroutines`.

Arrays *cannot* be declared inside the body of a function or gate. All arrays
*must* be declared within the global scope of the program.
Indexing of arrays is n-based *i.e.*, negative indices are allowed.
The index ``-1`` means the last element of the array, ``-2`` is the second to
last, and so on, with ``-n`` being the first element of an n-element array.
Multi-dimensional arrays (as in the example above) are allowed, with a maximum
of 7 total dimensions. The subscript operator ``[]`` is used for element access,
and for multi-dimensional arrays subarray accesses can be specified using a
comma-delimited list of indices (*e.g.* ``myArr[1, 2, 3]``), with the outer
dimension specified first.

For interoperability, the standard
ways of declaring quantum registers and bit registers are equivalent to the
array syntax version (*i.e.* ``qubit[5] q1;`` is the same as
``array[qubit, 5] q1;``).
Assignment to elements of arrays, as in the examples above, acts as expected,
with the left-hand side of the assignment operating as a reference, thereby
updating the values inside the original array. For multi-dimensional arrays,
the shape and type of the assigned value must match that of the reference.

.. code-block::

   array[int[8], 3] aa;
   array[int[8], 4, 3] bb;

   bb[0] = aa; // all of aa is copied to first element of bb
   bb[0, 1] = aa[2] // last element of aa is copied to one element of bb

   bb[0] = 1 // error - shape mismatch

Arrays may be passed to subroutines and externs. For more details, see
:any:`arrays-in-subroutines`.

Types related to timing
-----------------------

Duration
~~~~~~~~

We introduce a ``duration`` type to express timing.
Durations can be assigned with expressions including timing literals.
``durationof()`` is an intrinsic function used to reference the
duration of a calibrated gate.

.. code-block::

   duration one_second = 1000ms;
   duration thousand_cycles = 1000dt;
   duration two_seconds = one_second + 1s;
   duration c = durationof({x $3;});

``duration`` is further discussed in :any:`duration-and-stretch`

Stretch
~~~~~~~

We further introduce a ``stretch`` type which is a sub-type of ``duration``. ``stretch`` types
have variable non-negative duration that is permitted to grow as necessary
to satisfy constraints. Stretch variables are resolved at compile time
into target-appropriate durations that satisfy a user’s specified design
intent.

``stretch`` is further discussed in :any:`duration-and-stretch`

Aliasing
--------

The ``let`` keyword allows declared quantum bits and registers to be referred to by
another name as long as the alias is in scope.

.. code-block::

  qubit[5] q;
  // myreg[0] refers to the qubit q[1]
  let myreg = q[1:4];

Note that :ref:`physical qubits <physical-qubits>` are not declared and so cannot be aliased.

Index sets and slicing
----------------------

Register concatenation and slicing
----------------------------------

Two or more registers of the same type (i.e. classical or quantum) can
be concatenated to form a register of the same type whose size is the
sum of the sizes of the individual registers. The concatenated register
is a reference to the bits or qubits of the original registers. The
statement ``a ++ b`` denotes the concatenation of registers ``a`` and ``b``. A register cannot
be concatenated with any part of itself.

Classical and quantum registers can be indexed in a way that selects a
subset of (qu)bits, i.e. by an index set. A register so indexed is
interpreted as a register of the same type but with a different size.
The register slice is a reference to the original register. A register
cannot be indexed by an empty index set.

Similarly, classical arrays can be indexed using index sets. See :any:`array-slicing`.

An index set can be specified by a single integer (signed or unsigned), a
comma-separated list of integers contained in braces ``{a,b,c,…}``, or a range.
Ranges are written as ``a:b`` or
``a:c:b`` where ``a``, ``b``, and ``c`` are integers (signed or unsigned).
The range corresponds to the set :math:`\{a, a+c, a+2c, \dots, a+mc\}`
where :math:`m` is the largest integer such that :math:`a+mc\leq b` if
:math:`c>0` and :math:`a+mc\geq b` if :math:`c<0`. If :math:`a=b` then
the range corresponds to :math:`\{a\}`. Otherwise, the range is the
empty set. If :math:`c` is not given, it is assumed to be one, and
:math:`c` cannot be zero. Note the index sets can be defined by
variables whose values may only be known at run time.

.. code-block::

   qubit[2] one;
   qubit[10] two;
   // Aliased register of twelve qubits
   let concatenated = one ++ two;
   // First qubit in aliased qubit array
   let first = concatenated[0];
   // Last qubit in aliased qubit array
   let last = concatenated[-1];
   // Qubits zero, three and five
   let qubit_selection = two[{0, 3, 5}];
   // First seven qubits in aliased qubit array
   let sliced = concatenated[0:6];
   // Every second qubit
   let every_second = concatenated[0:2:12];
   // Using negative ranges to take the last 3 elements
   let last_three = two[-4:-1];
   // Concatenate two alias in another one
   let both = sliced ++ last_three;

Classical value bit slicing
---------------------------

A subset of classical values (int, uint, and angle) may be accessed at the bit
level using index sets similar to register slicing. The bit slicing operation
always returns a bit array of size equal to the size of the index set.

.. code-block::

   int[32] myInt = 15; // 0xF or 0b1111
   bit[1] lastBit = myInt[0]; // 1
   bit[1] signBit = myInt[31]; // 0
   bit[1] alsoSignBit = myInt[-1]; // 0

   bit[16] evenBits = myInt[0:2:31]; // 3
   bit[16] upperBits = myInt[-16:-1];
   bit[16] upperReversed = myInt[-1:-16];

   myInt[4:7] = "1010"; // myInt == 0xAF

Bit-level access is still possible with elements of arrays. It is suggested that
multi-dimensional access be done using the comma-delimited version of the
subscript operator to reduce confusion. With this convention nearly all
instances of multiple subscripts ``[][]`` will be bit-level accesses of array
elements.

.. code-block::

   array[int[32], 5] intArr = {0, 1, 2, 3, 4};
   // Access bit 0 of element 0 of intArr and set it to 1
   intArr[0][0] = 1;
   // lowest 5 bits of intArr[4] copied to b
   bit[5] b = intArr[4][0:4];

.. _array-slicing:

Array concatenation and slicing
-------------------------------

Two or more classical arrays of the same fundamental type can be
concatenated to form an array of the same type whose size is the
sum of the sizes of the individual arrays. Unlike with qubit registers, this operation
copies the contents of the input arrays to form the new (larger) array. This means that
arrays *can* be concatenated with themselves. However, the array concatenation
operator is forbidden to be used directly in the argument list of a subroutine
or extern call. If a concatenated array is to be passed to a subroutine then it
should be explicitly declared and assigned the concatenation.

.. code-block::

   array[int[8], 2] first = {0, 1};
   array[int[8], 3] second = {2, 3, 4};

   array[int[8], 5] concat = first ++ second;
   array[int[8], 4] selfConcat = first ++ first;

   array[int[8], 2] secondSlice = second[1:2]; // {3, 4}

   // slicing with assignment
   second[1:2] = first[0:1]; // second == {2, 0, 1}

   array[int[8], 4] third = {5, 6, 7, 8};
   // combined slicing and concatenation
   selfConcat[0:3] = first[0:1] ++ third[1:2];
   // selfConcat == {0, 1, 6, 7}

   subroutine_call(first ++ third) // forbidden
   subroutine_call(selfConcat) // allowed

Arrays can be sliced just like quantum registers using a range ``a:b:c`` 
and can be indexed using an integer but cannot be indexed by a a comma-separated 
list of integers contained in braces ``{a,b,c,…}``. Slicing uses
the subscript operator ``[]``, but produces an array (or reference in the case
of assignment) with the same number of dimensions as the given identifier.
Array slicing is syntactic sugar for concisely expressing for loops over
multi-dimensional arrays.
For sliced assignments, as with non-sliced assignments, the shapes and types of
the slices must match.

.. code-block::

   int[8] scalar;
   array[int[8], 2] oneD;
   array[int[8], 3, 2] twoD; // 3x2
   array[int[8], 3, 2] anotherTwoD; // 3x2
   array[int[8], 4, 3, 2] threeD; // 4x3x2
   array[int[8], 2, 3, 4] anotherThreeD; // 2x3x4

   threeD[0, 0, 0] = scalar; // allowed
   threeD[0, 0] = oneD; // allowed
   threeD[0] = twoD; // allowed

   threeD[0] = oneD; // error - shape mismatch
   threeD[0, 0] = scalar // error - shape mismatch
   threeD = anotherThreeD // error - shape mismatch

   twoD[1:2] = anotherTwoD[0:1]; // allowed
   twoD[1:2, 0] = anotherTwoD[0:1, 1]; // allowed

.. _castingSpecifics:
.. _implicit-promotion-rules:

Casting specifics
-----------------

The classical types are divided into the 'standard' classical types (bool, int,
uint, float, and complex) that exist in languages like C, and the 'special'
classical types (bit, angle, duration, and stretch) that do not.
The standard types follow rules that mimic those of C99 for `promotion and
conversion <https://en.cppreference.com/w/c/language/conversion>`_ in mixed
expressions and assignments.

If values with two different types are used as the operands of a binary
operation, the lesser of the two types is cast to the greater of the two.  All
``complex`` are greater than all ``float``, and all ``complex`` and all
``float`` are greater than all ``int`` or ``uint``.  Within each level of
``complex`` and ``float``, types with greater width are greater than types with
lower width.  For more information, see the `usual arithmetic conversions in C
<https://en.cppreference.com/w/c/language/conversion#Usual_arithmetic_conversions>`_.

The rules for rank of integer conversions mimic those of C99.  For more, see
`integer promotions <https://en.cppreference.com/w/c/language/conversion#Integer_promotions>`_, and
`integer conversions <https://en.cppreference.com/w/c/language/conversion#Integer_conversions>`_.

Standard and special classical types
may only mix in expressions with operators defined for those mixed types,
otherwise explicit casts must be provided, unless otherwise noted (such as for
assigning float values or expressions to angles).
Additionally, angle values will be implicitly promoted or converted in the same manner as
unsigned integers when mixed with or assigned to angle values with differing
precision.

In general, for any cast between standard types that results in loss of
precision, if the source value is larger than can be represented in the target
type, the exact behavior is implementation specific and must be documented by
the vendor.

Allowed casts
~~~~~~~~~~~~~

.. role:: rbg
.. role:: gbg
.. role:: center

+--------------+--------------------------------------------------------------------------------------------------------+
|              |                                       :center:`Casting To`                                             |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| Casting From | bool       | int        | uint       | float       | angle      | bit        | duration   | qubit      |
+==============+============+============+============+=============+============+============+============+============+
| **bool**     | :center:`-`| :gbg:`Yes` | :gbg:`Yes` | :gbg:`Yes`  | :rbg:`No`  | :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **int**      | :gbg:`Yes` | :center:`-`| :gbg:`Yes` | :gbg:`Yes`  | :rbg:`No`  | :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **uint**     | :gbg:`Yes` | :gbg:`Yes` | :center:`-`| :gbg:`Yes`  | :rbg:`No`  | :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **float**    | :gbg:`Yes` | :gbg:`Yes` | :gbg:`Yes` | :center:`-` | :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **angle**    | :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  | :rbg:`No`   | :center:`-`| :gbg:`Yes` | :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **bit**      | :gbg:`Yes` | :gbg:`Yes` | :gbg:`Yes` | :rbg:`No`   | :gbg:`Yes` | :center:`-`| :rbg:`No`  | :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **duration** | :rbg:`No`  | :rbg:`No`  | :rbg:`No`  | :rbg:`No*`  | :rbg:`No`  | :rbg:`No`  | :center:`-`| :rbg:`No`  |
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+
| **qubit**    | :rbg:`No`  | :rbg:`No`  | :rbg:`No`  | :rbg:`No`   | :rbg:`No`  | :rbg:`No`  | :rbg:`No`  | :center:`-`|
+--------------+------------+------------+------------+-------------+------------+------------+------------+------------+

\*Note: ``duration`` values can be converted to ``float`` using the division operator. See :ref:`divideDuration`

Casting from bool
~~~~~~~~~~~~~~~~~

``bool`` values cast from ``false`` to ``0.0`` and from ``true`` to ``1.0`` or
an equivalent representation. ``bool`` values can only be cast to ``bit[1]``
(a single bit), so explicit index syntax must be given if the target ``bit``
has more than 1 bit of precision.

Casting from int/uint
~~~~~~~~~~~~~~~~~~~~~

``int[n]`` and ``uint[n]`` values cast to the standard types mimicking C99
behavior. Casting to ``bool`` values follows the convention ``val != 0``.
As noted above, if the value is too large to be represented in the
target type the result is implementation-specific. However,
casting between ``int[n]`` and ``uint[n]`` is expected to preserve the bit
ordering, specifically it should be the case that ``x == int[n](uint[n](x))``
and vice versa. Casting to ``bit[m]`` is only allowed when ``m==n``. If the target
``bit`` has more or less precision, then explicit slicing syntax must be given.
As noted, the conversion is done assuming a little-endian 2's complement
representation.

Casting from float
~~~~~~~~~~~~~~~~~~

``float[n]`` values cast to the standard types mimicking C99 behavior (*e.g.*
discarding the fractional part for integer-type targets). As noted above,
if the value is too large to be represented in the
target type the result is implementation-specific.

Casting a ``float[n]`` value to an ``angle[m]`` involves finding the nearest
representable value modulo :math:`\text{float}_n(2\pi)`, where ties between two
possible representations are resolved by choosing to have zero in the
least-significant bit (*i.e.* round to nearest, ties to even).  Casting the
floating-point values ``inf``, ``-inf`` and all representations of ``NaN`` to
``angle[m]`` is not defined.

For example, given the double-precision floating-point value::

   // The closest double-precision representation of 2*pi.
   const float[64] two_pi = 6.283185307179586
   // For double precision, we have
   //   (two_pi * (127./512.)) / two_pi == (127./512.)
   // exactly.
   float[64] f = two_pi * (127. / 512.)

the result of the cast ``angle[8](f)`` should have the bitwise representation
``"01000000"`` (which represents the exact angle
:math:`2\pi\cdot\frac{64}{256} = \frac\pi2`), despite ``"00111111"``
(:math:`2\pi\cdot\frac{63}{256}`) being equally close, because of the
round-to-nearest ties-to-even behaviour.

Casting from angle
~~~~~~~~~~~~~~~~~~

``angle[n]`` values cast to ``bool`` using the convention ``val != 0``.  Casting
to ``bit[m]`` values is only allowed when ``n==m``, otherwise explicit slicing
syntax must be provided.  When casting to ``bit[m]``, the value is a direct
copy of the bit pattern using the same little-endian ordering :ref:`as described
above <angle-type>`.

When casting between angles of differing precisions (``n!=m``): if the target
has more significant bits, then the value is padded with ``m-n`` least
significant bits of ``0``; if the target has fewer significant bits, then
there are two acceptable behaviors that can be supported by compilers:
rounding and truncation. For rounding the value is rounded to the nearest
value, with ties going to the value with the even least significant bit.
Trunction is likely to have more hardware support. This behavior can be
controlled by the use of a ``#pragma``.

Casting from bit
~~~~~~~~~~~~~~~~

``bit[n]`` values cast to ``bool`` using the convention ``val != 0``. Casting to
``int[m]`` or ``uint[m]`` is done assuming a little endian 2's complement
representation, and is only allowed when ``n==m``, otherwise explicit slicing
syntax must be given. Likewise, ``bit[n]`` can only be cast to ``angle[m]``
when ``n==m``, in which case an exact per-bit copy is done using little-endian
bit order. Finally, casting between bits of differing precisions is not
allowed, explicit slicing syntax must be given.

.. _divideDuration:

Converting duration to other types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Casting from or to duration values is not allowed, however, operations on
durations that produce values of different types is allowed. For example,
dividing a duration by a duration produces a machine-precision ``float``.

.. code-block::

   duration one_ns = 1ns;
   duration a = 500ns;
   float a_in_ns = a / one_ns;  // 500.0

   duration one_s = 1s;
   float a_in_s = a / one_s; // 5e-7

