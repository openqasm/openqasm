for myvar in { 1, 2, 3 };
for myvar1, myvar2 in { 1, 2, 3 } { x $0; }
for myvar in { x $0; } { x $0; }
for myvar in for { x $0; }
for myvar { x $0; }
for (true) { x $0; }
for { x $0; }
for for in { 1, 2, 3 } { x $0; }
for in { 1, 2, 3 } { x $0; }
while true { x $0; }
while (true) (true) { x $0; }
while x in { 1, 2, 3 } { x $0; }
while (true);
