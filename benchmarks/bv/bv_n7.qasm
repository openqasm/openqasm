//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Bernstein-Vazirani with 7 qubits.
//Hidden string is 111111
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[7];
creg cr[6];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
h qr[4];
h qr[5];
x qr[6];
h qr[6];
barrier qr[0],qr[1],qr[2],qr[3],qr[4],qr[5],qr[6];
cx qr[0],qr[6];
cx qr[1],qr[6];
cx qr[2],qr[6];
cx qr[3],qr[6];
cx qr[4],qr[6];
cx qr[5],qr[6];
barrier qr[0],qr[1],qr[2],qr[3],qr[4],qr[5],qr[6];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
h qr[4];
h qr[5];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
measure qr[4] -> cr[4];
measure qr[5] -> cr[5];
