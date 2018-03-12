//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Bernstein-Vazirani with 5 qubits.
//Hidden string is 1111
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[5];
creg cr[4];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
x qr[4];
h qr[4];
barrier qr[0],qr[1],qr[2],qr[3],qr[4];
cx qr[0],qr[4];
cx qr[1],qr[4];
cx qr[2],qr[4];
cx qr[3],qr[4];
barrier qr[0],qr[1],qr[2],qr[3],qr[4];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
