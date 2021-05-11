// One randomized benchmarking sequence
OPENQASM 3;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

reset q;
h q[0];
barrier q;
cz q[0], q[1];
barrier q;
s q[0];
cz q[0], q[1];
barrier q;
s q[0];
z q[0];
h q[0];
barrier q;
measure q -> c;
