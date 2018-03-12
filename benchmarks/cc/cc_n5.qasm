//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Counterfeit coin finding with 4 coins.
//The false coin is 3
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[5];
creg cr[5];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
cx qr[0],qr[4];
cx qr[1],qr[4];
cx qr[2],qr[4];
cx qr[3],qr[4];
measure qr[4] -> cr[4];
if(cr==0) x qr[4];
if(cr==0) h qr[4];
if(cr==16) h qr[0];
if(cr==16) h qr[1];
if(cr==16) h qr[2];
if(cr==16) h qr[3];
barrier qr[0],qr[1],qr[2],qr[3],qr[4];
if(cr==0) cx qr[3],qr[4];
barrier qr[0],qr[1],qr[2],qr[3],qr[4];
if(cr==0) h qr[0];
if(cr==0) h qr[1];
if(cr==0) h qr[2];
if(cr==0) h qr[3];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
