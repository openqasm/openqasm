// Repetition code gate teleportation
OPENQASM 3;
include "stdgates.inc";

// declarations
const n = 3;
kernel vote bit[n] -> bit;

def logical_meas qubit[3]:d -> bit {
    bit c[3];
    bit r;
    measure d -> c;
    vote c -> r;
    return r;
}

qubit q[3];
qubit a[3];
bit r;

// prep magic state
rz(pi/4) a;

// entangle two logical registers
cx q, a;

// measure out the ancilla
logical_meas a -> r;

// if we get a logical |1> then we need to apply a logical Z correction
if (r == 1) z q;
