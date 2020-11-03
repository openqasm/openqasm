Directives
==========

OpenQASM supports a directive mechanism that allows other information to
be included in the program. A directive begins with ``#pragma`` and
terminates at the end of the line. Directives can provide annotations
that give additional information to compiler passes and the target
system or simulator. Ideally the meaning of the program does not change
if some or all of the directives are ignored, so they can be interpreted
at the discretion of the consuming process.
