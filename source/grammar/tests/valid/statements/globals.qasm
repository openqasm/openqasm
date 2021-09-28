OPENQASM 3;
include 'stdgates.inc';
input int[8] myvar;
output int[8] myvar;
def myfunc() -> int[8] { return 12; }
extern myfunc () -> int[8];
gate ccy a, b, c { ctrl @ ctrl @ y a, b, c; }
defcalgrammar "openpulse";
defcal x $0 { }
