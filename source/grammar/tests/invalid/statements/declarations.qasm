// Not specifying the variable.
float;
uint[8];
qreg[4];
creg[4];
complex[float[32]];

// Incorrect designators.
int myvar;
int[8, 8] myvar;
uint myvar;
uint[8, 8] myvar;
float myvar;
float[8, 8] myvar;
angle myvar;
angle[8, 8] myvar;
bool[4] myvar;
bool[4, 4] myvar;
bit[4, 4] myvar;
creg[2] myvar;
creg[2, 2] myvar;
qreg[2] myvar;
qreg[2, 2] myvar;
complex myvar;
complex[float] myvar;
complex[32] myvar;
complex[mytype] myvar;
complex[float[32], float[32]] myvar;
complex[qreg] myvar;
complex[creg] myvar;
complex[qreg[8]] myvar;
complex[creg[8]] myvar;

// Invalid identifiers.
int[8] int;
int[8] def;
int[8] 0;
int[8] input;

// Bad assignments.
int[8] myvar = end;
int[8] myvar =;
float[32] myvar_f = int[32] myvar_i = 2;

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
