if true x $0;
if false { x $0; }
if (myvar += 1) { x $0; }
if (int[8] myvar = 1) { x $0; }
if (true);
if (true) else x $0;
if (true) else (false) x $0;
if (reset $0) { x $1; }
