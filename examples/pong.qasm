/*
 * 0 |   CNOT   |
 * 1 |   CNOT   |
 * 2 PPPMMMMMMPPP
 */
defcalgrammar "openpulse";

defcal pong(angle[32] amp, duration dur) $q {
    play d0, gaussian(amp, dur)
}

defcal pong_cx(angle[32] amp) $q0, $q1, $q2 {
    barrier $q0, $q1, $q2;
    cross-res(pi/4) $q0, $q1
    x(pi) $q0;  // this is a defcal
    cross-res(-pi/4) $q0, $q1;
    glue[1]-pong(amp) $q1;
    glue[2]-pong(-amp) $q1;
    glue[1]-pong(amp) $q1;
    barrier $q0, $q1, $q2;
}

barrier $0, $1, $2;
glue[1]-delay[0] $0;    // these stretchable delays would be inserted by a high-level scheduling pass.
glue[1]-delay[0] $1;    // it should be possible to write regular QASM using those ponged CNOTs
glue[1]-delay[0] $2;    // even if you don't care how the whole program is aligned (left of right)
h $0;
pong(0.5, 10dt) $0 - pong_cx(0.5) $0, $1, $2;
barrier $0, $1, $2;


//boxto conditional, anonymous subroutine (named boxto not supported)

duration maxdur = 1us;

qubit[2] q;
barrier q[0], q[1];
slowgate q[0];
stretch s;
delay[s] q[1];
h q[1];
measure q[1] -> c[0];
delay[s] q[1];
box [maxdur] { // fixed-duration anonymous subroutine
    if (c==0) U(0.1, 0.2, 0.3) q[1];  // duration depends on result of measurement
    delay[s] q[1];                 // glue to allow to stretch (can be implicit)
} // throw runtime error if `box` does not conclude by maxdur
delay[s] q[1];
barrier q[0], q[1];
