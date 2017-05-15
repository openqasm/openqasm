// Name of Experiment: Deutsch Algorithm v3
// Description: Simple two qubit implementation of Deutsch algorithm. It shows that, for a given function f, in order to know value of f(0) xor f(1) can be computed using 1 query. If result is 1, f is balanced, otherwise it is constant funcion

OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[5];

x q[4];
h q[3];
h q[4];
cx q[3],q[4];
h q[3];
measure q[3] -> c[3];
