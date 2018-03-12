//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Bernstein-Vazirani with 4 qubits.
//Hidden string is 111
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[4];
creg cr[3];
h qr[0];
h qr[1];
h qr[2];
x qr[3];
h qr[3];
barrier qr[0],qr[1],qr[2],qr[3];
cx qr[0],qr[3];
cx qr[1],qr[3];
cx qr[2],qr[3];
barrier qr[0],qr[1],qr[2],qr[3];
h qr[0];
h qr[1];
h qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
