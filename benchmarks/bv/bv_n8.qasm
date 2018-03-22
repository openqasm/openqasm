//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Bernstein-Vazirani with 8 qubits.
//Hidden string is 1111111
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[8];
creg cr[7];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
h qr[4];
h qr[5];
h qr[6];
x qr[7];
h qr[7];
barrier qr[0],qr[1],qr[2],qr[3],qr[4],qr[5],qr[6],qr[7];
cx qr[0],qr[7];
cx qr[1],qr[7];
cx qr[2],qr[7];
cx qr[3],qr[7];
cx qr[4],qr[7];
cx qr[5],qr[7];
cx qr[6],qr[7];
barrier qr[0],qr[1],qr[2],qr[3],qr[4],qr[5],qr[6],qr[7];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
h qr[4];
h qr[5];
h qr[6];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
measure qr[4] -> cr[4];
measure qr[5] -> cr[5];
measure qr[6] -> cr[6];
