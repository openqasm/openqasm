.. _sec:spec:

Language
========

Hereafter, OpenQASM refers to the extended language we now describe. The
human-readable form of OpenQASM is a simple C-like textual language. By
that we mean that statements are separated by semicolons and whitespace
is ignored. In other respects, OpenQASM diverges quite significantly from
C, reflecting its dual nature as sometimes an assembly language and
sometimes as a hardware description language. The language is case
sensitive. Appendix `[app:summary] <#app:summary>`__ summarizes the
language statements, Appendix `[app:grammar] <#app:grammar>`__ specifies
the grammar, and Appendix `[app:semantics] <#app:semantics>`__ gives formal
semantics.

.. toctree::

   comments
   types
   gates
   insts
   classical
   subroutines
   directives
   delays
   pulses
