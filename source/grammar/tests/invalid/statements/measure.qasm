measure $0, $1;
a[0:1] = measure $0, $1;
a = measure $0 -> b;
creg a[1] = measure $0;
measure $0 -> creg a[1];
measure $0 -> bit[1] a;
// Measure can't be used in sub-expressions.
a = 2 * measure $0;
a = (measure $0) + (measure $1);
