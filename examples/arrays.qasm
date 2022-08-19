OPENQASM 3.0;

// ==================
// Array declarations
// ==================

// Declare 'my_ints' to be a 1D array of 8-bit signed integers, where the index
// runs from 0 to 15.
array[int[8], 16] my_ints;

// Declare 'my_doubles' to be a 2D array of double-precision floating-point
// values, where the first index runs from 0 to 7 and the second from 0 to 3.
array[float[64], 8, 4] my_doubles;

// Initialise a 1D array with fixed values.
array[uint[32], 4] my_defined_uints = {5, 6, 7, 8};

// Initialise a 2D array with fixed values.
array[float[32], 4, 2] my_defined_floats = {
    {0.5, 0.5},
    {1.0, 2.0},
    {-0.4, 0.7},
    {1.3, -2.1e-2}
};

// Initialise an array using a row of another array.  Note that this copies the
// data; changes to the values in `my_defined_float_row` will not affect
// `my_defined_floats`.
array[float[32], 2] my_defined_float_row = my_defined_floats[0];

// Arrays can be defined in terms of compile-time constant dimension sizes, and
// can use expressions in the slots of their initialisers.
const uint[8] DIM_SIZE = 2;
array[int[8], DIM_SIZE, DIM_SIZE] all_ones = {{2+3, 4-1}, {3+8, 12-4}};


// =============================
// Array indexing and operations
// =============================

// Use `[]` notation to access array elements.  The dimensions are
// comma-separated.
uint[8] a = my_defined_uints[0];
float[32] b = my_defined_floats[2, 1];

// The same notation is used in simple assignments.
my_defined_uints[1] = 5;
my_defined_floats[3, 0] = -0.45;

// In both, the indices can be (non-constant) expressions.
my_defined_uints[a - 1] = a + 1;

// Assignments can also be done using an array, or array slice, on the left-hand
// side, provided the right-hand side evaluates to an array of exactly the same
// shape.  The assignment is done by copy, so subsequent changes to either of
// the two parts will not affect the other.
my_defined_floats[2] = my_defined_float_row;

// You can also use the slice notation to set elements.  Beware that it is
// generally a logical error to read and write from overlapping slices at the
// same time, and that OpenQASM 3 makes no guarantees about which order the data
// will be read from and written to.  You might clobber data if you overlap.
my_defined_floats[0:1] = my_defined_floats[2:3];

// The ``sizeof`` operator returns the size of an array's dimension.
const uint[32] dimension = sizeof(my_defined_uints);  // assigns 4.

// The ``sizeof`` operator can also be used in two-argument form, where the
// second argument is the index of the dimension, counting from 0.
const uint[32] first_dimension = sizeof(my_doubles, 0);  // returns 8
const uint[32] second_dimension = sizeof(my_doubles, 1);  // returns 4

// If the second argument is omitted from ``sizeof`` and the given array is
// multi-dimensional, it defaults to returning the first dimension, so
// ``sizeof(my_array) == sizeof(my_array, 0)`` in all circumstances.
const uint[32] first_dimension = sizeof(my_doubles);  // still 8.


// =====================
// Arrays in subroutines
// =====================

// Array arguments have a mandatory ``readonly`` or ``mutable`` specifier when
// defined in a subroutine argument list.  This is because arrays are passed to
// subroutines by reference, not by value, so modifications will propagate back
// to the original data.  Such modifications are only allowed for ``mutable``
// references, not ``readonly``.
def copy_3_bytes(readonly array[uint[8], 3] in_array, mutable array[uint[8], 3] out_array) {
    // Within this block, ``in_array`` can be read from, but not written to,
    // whereas ``out_array`` can be both read from and written to.
}

// When specifying array subroutine parameters, there is a second format where
// the sizes of the dimensions are not given explicitly, only the number of
// dimensions.  This is where the ``sizeof`` operator is most useful.  In these
// cases, `sizeof` is _not_ a compile-time constant.
def multi_dimensional_input(readonly array[int[32], #dim=3] my_array) {
    uint[32] dimension_0 = sizeof(my_array, 0);
    uint[32] dimension_1 = sizeof(my_array, 1);
    uint[32] dimension_2 = sizeof(my_array, 2);
}
