OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];

// Bob's input
h q[0];
// Alice's input
h q[1];
// Bob's output
h q[2];
// Alice's output
cx q[2],q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];

// Bob's strategy
if (c==0) ry(pi/4) q[2];
if (c==2) ry(pi/4) q[2];
if (c==1) ry(-pi/4) q[2];
if (c==3) ry(-pi/4) q[2];

// Alice's strategy
if (c==2) ry(pi/2) q[3];
if (c==3) ry(pi/2) q[3];

// 85% correct magic
measure q[2] -> c[2];
measure q[3] -> c[3];