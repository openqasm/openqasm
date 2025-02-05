Directives
==========

OpenQASM supports directive mechanisms that allow other information to
be included in the program. Directives are either pragmas or annotations.
Both are used to supply additional information to the compiler passes and the
target system or simulator. Ideally the meaning of the program does not change
if some or all of the directives are ignored, so they can be interpreted
at the discretion of the consuming process.

Pragma and annotation namespacing
---------------------------------

It is intended that different implementators of the specification might
define their own pragmas and annotations. This creates the possibility that
different implementations might define pragmas or annotations that collide.

To avoid such collisions we recommend that implementations namespace their
pragmas and annotations as follows:

- Pragmas start with `pragma <namespace>.<name>(.<name>)*`.
- Annotations start with `@<namespace>.<name>(.<name>)*`.

Where `namespace` and `name` are valid OpenQASM identifiers.

If the pragma or annotation takes additional arguments the
final `<name>` should be followed by a single space before the
additional text.

The namespace should be a short name that identifies the organization that
defines behaviour of the pragmas and annotations contained within it.

The namespace `openqasm` is reserved for future use by the OpenQASM
specification.


Pragmas
-------

Pragma directives start with ``pragma`` and continue to the end of line. The
text after ``pragma`` is a single string, and parsing is left to the specific
implementation, although implementors are encourage to use the namespacing
described above.

Implementations may optionally choose to support the older ``#pragma`` keyword
as a custom extension.

Pragmas should be processed as soon as they are encountered; if a
pragma is not supported by a compiler pass it should be ignored and preserved
intact for future passes.  Pragmas should avoid stateful or positional
interactions to avoid unexpected behaviors between included source files. If the
position is relevant to a pragma, an annotation should be used instead.

Pragmas are useful for extending OpenQASM functionality that is not described in
this specification, such as adding directives to a simulator.

\*Note: The following examples are simply possible implementations, this
specification does not define any pragmas. Please consult your tool's
documentation for supported pragmas.

.. code-block::

   pragma qiskit.simulator noise model "qpu1.noise"

Pragmas can also be used to specify system-level information or assertions for
the entire circuit.

.. code-block::

   OPENQASM 3.0;

   // Attach billing information
   pragma ibm.user alice account 12345678

   // Assert that the QPU is healthy to run this circuit
   pragma ibm.max_temp qpu 0.4

   qubit[2] q;


Annotations
-----------

Annotations can be added to supply additional information to the following
OpenQASM ``statement`` as defined in the grammar. Annotations will start with a
``@`` symbol, have a dotted list of identifying keywords and continue to the end
of the line.

Multiple annotations may be added to a single statement. No ordering or
interaction between annotations are prescribed by this specification.

\*Note: The following examples are simply possible implementations, this
specification does not define any annotations. Please consult your tool's
documentation for supported annotations.

.. code-block::

   // Manage port binding on a physical device
   @bind IOPORT[3:2]
   input bit[2] control_flags;

   // Instruct compiler to create a reversible version of the function
   @openqasm.reversible
   gate multiply a, b, x {
      x = a * b;
   }

   // Prevent swap insertion
   @openqasm.noswap
   box {
      rx(pi) q[0];
      cnot q[0], q[3];
   }

   // Apply multiple annotations
   @openqasm.crosstalk
   @openqasm.noise profile "gate_noise.qnf"
   defcal noisy_gate $0 $1 { ... }


Input/output
============

OpenQASM introduces features targeted to support near-time computation, in
the form of parameterized circuits. These features are modifiers ``input``
and ``output``, which allow OpenQASM3 circuits to accept input parameters
and return select output parameters.

The ``input`` modifier can be used to indicate that one or more variable
declarations represent values which will be provided at run-time, upon
invocation. This allows the programmer to use the same compiled circuits
which only differ in the values of certain parameters. For backward compatibility,
OpenQASM3 does not require an ``input`` declaration to be provided. When
an ``input`` declaration is provided, the compiler produces an executable
that leaves these free parameters unspecified: a circuit run would take as
input both the executable and some choice of the parameters.

Similarly, the ``output`` modifier can be used to indicate that one or more variables
are to be provided as an explicit output of the quantum procedure. Note that
OpenQASM 2 did not allow the programmer to specify that only a subset of its
variables should be returned as output, and so it would return all classical
variables (which were all creg variables) as output. For compatibility, 
OpenQASM 3 does not require an output declaration to be provided: in this 
case it assumes that all of the declared variables are to be returned as
output. If the programmer provides one or more output declarations, then only
those variables described as outputs will be returned as an output of the 
quantum process. A variable may not be marked as both input and output.

The input and output modifiers allow the programmer to more easily write 
variational quantum algorithms: a quantum algorithm with some free parameters,
which may be run many times with different parameter values which are determined
by a classical optimiser at near-time. Rather than write a circuit which
generates a new sequence of operations for each run, OpenQASM 3 allows such
circuits to be expressed as a single program with input parameters. This 
allows the programmer to communicate many different circuits with a single
file, which only has to be compiled once, amortizing the cost of compilation
across many runs. For an example, we may consider a parameterized circuit which
performs a measurement in a basis given by an input parameter:

.. code-block::

   input int basis; // 0 = X basis, 1 = Y basis, 2 = Z basis
   output bit result;
   qubit q;

   // Some complicated circuit...

   if (basis == 0) h q;
   else if (basis == 1) rx(π/2) q;
   result = measure q;

For a second example, consider the Variable Quantum Eigensolver (VQE) algorithm :cite:`peruzzo2014variational`.
In this algorithm the same circuit is repeated
many times using different sets of free parameters to minimize an expectation 
value. The following is an example, in which there is also more than one input
variable:

.. code-block::

   input angle[32] param1;
   input angle[32] param2;
   qubit q;

   // Build an ansatz using the above free parameters, eg.
   rx(param1) q;
   ry(param2) q;

   // Estimate the expectation value and store in an output variable

The above example could also be written using an input array:

.. code-block::

   input array[angle[32], 2] params;
   qubit q;

   // Build an ansatz using the above free parameters, eg.
   rx(params[0]) q;
   ry(params[1]) q;

   // Estimate the expectation value and store in an output variable

The following Python pseudocode illustrates the differences between using and
not using parameterized circuits in a quantum program for the case of the VQE:

.. code-block:: python

   # Example without using parametric circuits:

   for theta in thetas:
       # Create an OpenQASM circuit with θ defined
       circuit = subsitute_theta(read("circuit.qasm"))

       # The slow compilation step is run on each iteration of the inner loop
       binary = compile_qasm(circuit)
       result = run_program(binary)

   # Example using parametric circuits:

   # parametric_circuit.qasm begins with the line "input angle θ;"
   circuit = read("parametric_circuit.qasm")

   # The slow compilation step only happens once
   binary = compile_qasm(circuit)

   for theta in thetas:
       # Each iteration of the inner loop is reduced to only running the circuit
       result = run_program(binary, θ=theta)
