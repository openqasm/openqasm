//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Bernstein-Vazirani with 3 qubits.
//Hidden string is 11
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[3];
creg cr[2];
h qr[0];
h qr[1];
x qr[2];
h qr[2];
barrier qr[0],qr[1],qr[2];
cx qr[0],qr[2];
cx qr[1],qr[2];
barrier qr[0],qr[1],qr[2];
h qr[0];
h qr[1];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
