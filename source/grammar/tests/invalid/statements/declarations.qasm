// Not specifying the variable.
float;
uint[8];
qreg[4];
creg[4];
complex[float[32]];

// Incorrect designators.
int[8, 8] myvar;
uint[8, 8] myvar;
float[8, 8] myvar;
angle[8, 8] myvar;
bool[4] myvar;
bool[4, 4] myvar;
bit[4, 4] myvar;
creg[2] myvar;
creg[2, 2] myvar;
qreg[2] myvar;
qreg[2, 2] myvar;
complex[32] myvar;
complex[mytype] myvar;
complex[float[32], float[32]] myvar;
complex[qreg] myvar;
complex[creg] myvar;
complex[qreg[8]] myvar;
complex[creg[8]] myvar;

// Bad array specifiers.
array myvar;
array[8] myvar;
array[not_a_type, 4] myvar;
array[int[8], int[8], 2] myvar;

// Invalid identifiers.
int[8] int;
int[8] def;
int[8] 0;
int[8] input;

// Bad assignments.
int[8] myvar = end;
int[8] myvar =;
float[32] myvar_f = int[32] myvar_i = 2;
// array initialiser uses {}
array[uint[8], 4] myvar = [4, 5, 6, 7];
// can't use arithmetic on the entire initialiser
array[uint[8], 4] myvar = 2 * {1, 2, 3, 4};
// backed arrays can't use #dim
array[uint[8], #dim=2] myvar;
// can't have more than one type specification
array[int[8], int[8]] myvar;

// Incorrect orders.
myvar: int[8];
myvar int[8];
int myvar[8];
uint myvar[8];
float myvar[32];

// Compound assignments.
int[8] myvar1, myvar2;
int[8] myvari, float[32] myvarf;
int[8] myvari float[32] myvarf;
