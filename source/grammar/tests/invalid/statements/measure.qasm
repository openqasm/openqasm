measure $0, $1;
a[0:1] = measure $0, $1;
a = measure $0 -> b;
creg a[1] = measure $0;
measure $0 -> creg a[1];
bit[1] a = measure $0;
measure $0 -> bit[1] a;
