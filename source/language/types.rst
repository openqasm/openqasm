.. role:: raw-latex(raw)
   :format: latex
..

Types and Casting
=================

.. _identifiers:

Identifiers
-----------

Identifiers must begin with a letter [A-Za-z], an underscore or an element from
the Unicode character categories Lu/Ll/Lt/Lm/Lo/Nl :cite:`noauthorUnicodeNodate`.
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
Sizes must always be constant positive integers. The label ``name[j]``
refers to a qubit of this register, where
:math:`j\in \{0,1,\dots,\mathrm{size}(\mathrm{name})-1\}` is an integer.
Quantum registers are static arrays of qubits
that cannot be dynamically resized.

The keyword ``qreg`` is included
for backwards compatibility and will be removed in the future.

Qubits are initially in an undefined state. A quantum ``reset`` operation is one
way to initialize qubit states.

All qubits are global variables.
Qubits cannot be declared within gates or subroutines. This simplifies OpenQASM
significantly since there is no need for quantum memory management.
However, it also means that users or compiler have to explicitly manage
the quantum memory.

Physical Qubits
~~~~~~~~~~~~~~~

While program qubits can be named, hardware qubits are referenced only
by the syntax ``$[NUM]``. For an ``n`` qubit system, we have physical qubit
references given by ``$0``, ``$1``, ..., ``$n-1``. These qubit types are
used in lower parts of the compilation stack when emitting physical
circuits. Physical qubits must not be declared and they are, as all the qubits, global variables.

.. code-block::

   // Declare a qubit
   qubit gamma;
   // Declare a qubit with a Unicode name
   qubit γ;
   // Declare a qubit register with 20 qubits
   qubit[20] qubit_array;
   // CNOT gate between physical qubits 0 and 1
   CX $0, $1;

Classical types
---------------

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
   // Declare and assign a rgister of bits with decimal value of 15
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
attached to an identifer or used as a cast operator. The keyword ``void`` is
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
followed by the letters ``im``.  There may be zero or more spaces between the
numeric component and the ``im`` component.  The type of this token is
``complex`` (its value has zero real component), and the component type is as
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

Const values
~~~~~~~~~~~~

To support mathematical expressions, immutable constants of any classical type
may be declared using the type modifier ``const``. On
declaration, they take their assigned value and cannot be redefined
within the same scope. These are constructed using an in-fix notation
and scientific calculator features such as scientific notation, real
arithmetic, logarithmic, trigonometric, and exponential functions
including ``sqrt``, ``floor``, ``ceiling``, ``log``, ``pow``, ``div``, ``mod`` and the built-in constant π. The
statement ``const type name = expression;`` defines a new constant. The expression on the right hand side
has a similar syntax as OpenQASM 2 parameter expressions; however,
previously defined constants can be referenced in later variable
declarations. ``const`` values are compile-time constants, allowing the
compiler to do constant folding and other such optimizations. Scientific
calculator-like operations on run-time values require extern function
calls as described later and are not available by default. Real
constants can be cast to other types, just like other values.

A standard set of built-in constants which are included in the default
namespace are listed in table `1 <#tab:real-constants>`__. These constants
are all of type ``float[64]``.

.. code-block::

   // Declare a constant
   const int my_const = 1234;
   // Scientific notation is supported
   const int[64] another_const = 1e12;
   // Constant expressions are supported
   const float[64] pi_by_2 = π / 2;
   // Constants may be cast to real-time values
   float[32] pi_by_2_val = float[32](pi_by_2)

.. container::
   :name: tab:real-constants

   .. table:: [tab:real-constants] Built-in real constants in OpenQASM3 of type ``float[64]``.

      +-------------------------------+--------------+--------------+---------------------+
      | Constant                      | Alphanumeric | Unicode      | Approximate Base 10 |
      +===============================+==============+==============+=====================+
      | Pi                            | pi           | π            | 3.1415926535...     |
      +-------------------------------+--------------+--------------+---------------------+
      | Tau                           | tau          | τ            | 6.283185...         |
      +-------------------------------+--------------+--------------+---------------------+
      | Euler’s number                | euler        | ℇ            | 2.7182818284...     |
      +-------------------------------+--------------+--------------+---------------------+

Note that `e` is a valid identifier. `e/E` are also used in scientific notation where appropriate.

Mathematical functions available for constant initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to simple arithmetic functions used in expressions initializing constants,
OpenQASM 3 offers the following built-in mathematical operators followed by
their argument expression in parentheses:

.. container::
   :name: tab:built-in-math

   .. table:: Built-in mathematical functions in OpenQASM3.

      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | Function | Input Range/Type, [...]           | Output Range/Type                    | Notes                                  |
      +==========+===================================+======================================+========================================+
      | arccos   | ``float`` on :math:`[-1, 1]`      | ``float`` on :math:`[0, \pi]`        |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | arcsin   | ``float`` on :math:`[-1, 1]`      | ``float`` on :math:`[-\pi/2, \pi/2]` |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | arctan   | ``float``                         | ``float`` on :math:`[-\pi/2, \pi/2]` |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | ceiling  | ``float``                         | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | cos      | (``float`` or ``angle``)          | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | exp      | ``float``                         | ``float``                            |                                        |
      |          |                                   |                                      |                                        |
      |          | ``complex``                       | ``complex``                          |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | floor    | ``float``                         | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | log      | ``float``                         | ``float``                            | Logarithm base :math:`e`               |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | mod      | ``int``, ``int``                  | ``int``                              |                                        |
      |          |                                   |                                      |                                        |
      |          | ``float``, (``int`` or ``float``) | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | popcount | ``bit[_]``, ``uint``              | ``uint``                             |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | pow      | ``int``, ``uint``                 | ``int``                              |                                        |
      |          |                                   |                                      |                                        |
      |          | ``float``, ``float``              | ``float``                            | For floating-point and complex values, |
      |          |                                   |                                      | the principal value is returned.       |
      |          | ``complex``, ``complex``          | ``complex``                          |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | rotl     | ``bit[n]``, (``int`` or ``uint``) | ``bit[n]``                           |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | rotr     | ``bit[n]``, (``int`` or ``uint``) | ``bit[n]``                           |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | sin      | (``float`` or ``angle``)          | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | sqrt     | ``float``                         | ``float``                            | Returns the principal root.            |
      |          |                                   |                                      |                                        |
      |          | ``complex``                       | ``complex``                          |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+
      | tan      | (``float`` or ``angle``)          | ``float``                            |                                        |
      +----------+-----------------------------------+--------------------------------------+----------------------------------------+

Literals
--------

There are five types of literals in OpenQASM 3, integer, float, boolean,
bit string, and timing.

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

The two boolean literals are the lowercase strings ``true`` and ``false``.

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

The ``let`` keyword allows quantum bits and registers to be referred to by
another name as long as the alias is in scope.

.. code-block::

  qubit[5] q;
  // myreg[0] refers to the qubit q[1]
  let myreg = q[1:4];

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
   // First six qubits in aliased qubit array
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

Arrays can be sliced just like quantum registers using index sets. Slicing uses
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

