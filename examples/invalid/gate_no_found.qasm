// name: Gate not found
// description: All gates should be declared before be used.
// section: TODO
OPENQASM 2.0;
qreg q[1];
w q;
creg c[1];
measure q->c;
