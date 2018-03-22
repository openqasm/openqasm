//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Counterfeit coin finding with 3 coins.
//The false coin is 1
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[4];
creg cr[4];
h qr[0];
h qr[1];
h qr[2];
cx qr[0],qr[3];
cx qr[1],qr[3];
cx qr[2],qr[3];
measure qr[3] -> cr[3];
if(cr==0) x qr[3];
if(cr==0) h qr[3];
if(cr==8) h qr[0];
if(cr==8) h qr[1];
if(cr==8) h qr[2];
barrier qr[0],qr[1],qr[2],qr[3];
if(cr==0) cx qr[1],qr[3];
barrier qr[0],qr[1],qr[2],qr[3];
if(cr==0) h qr[0];
if(cr==0) h qr[1];
if(cr==0) h qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
