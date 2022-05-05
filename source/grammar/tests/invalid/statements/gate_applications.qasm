U (1)(2) $0;
notmodifier @ x $0;
pow @ x $0;
pow(2, 3) @ x $0;
ctrl(2, 3) @ x $0, $1;
negctrl(2, 3) @ x $0, $1;
inv(1) @ ctrl @ x $0, $1;

// Global phase is defined in the grammar to be the last modifier.
gphase(pi) @ ctrl @ x $0, $1;
