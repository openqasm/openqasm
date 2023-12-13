# Nominations for the Technical Steering Committee election December 15, 2023

This document contains the nomination statements for each of the candidates for the TSC seats opening in 2024

[The electoral roll for this election](./contributors.md) can can be found in [`contributors.md`](./contributors.md).

The election will take place online using the [Belenios online voting platform](https://www.belenios.org/).

Three people will be elected, to join Lev Bishop (IBM), Dor Israeli (Quantum Machines), and Blake Johnson (IBM)  whose seats are not up for re-election this cycle.
Votes will be counted using the [Condorcet/Schulze method](https://en.wikipedia.org/wiki/Schulze_method) to produce a ranked list of the candidates.
The top three candidates will be elected to the TSC.
The election will close on Monday the 15th of January, 2024 at 12:00 UTC.

In alphabetical order, the candidates are:

## Erik Davis (AWS)

I am a software engineer at the AWS Center for Quantum Computing, where I serve as lead developer
for an in-house OpenQASM+OpenPulse compiler. I have worked on compiler toolchains or control
software at three quantum computing companies, with experience spanning multiple qubit architectures
(superconducting qubits & quantum dots), multiple levels of abstraction (gate-based and pulse-based
compilation), and multiple hardware backends (from commercial off-the-shelf waveform generators to
more boutique efforts).


OpenQASM is the premier language for describing quantum experiments, for both technical and social
reasons. As a matter of the language itself, the "two-level semantics" -- where gate-based circuits
may be mixed with pulse-based calibrations -- is well suited to the reality of quantum hardware
today. Just as significantly, the community surrounding the language offers tooling and support that
no single quantum effort could sustain independently. At AWS we have bet on OpenQASM for both of
these reasons.


The field of quantum computing never stands still. As a TSC member, my mission would be to steer
OpenQASM to comfortably meet the demands of increasingly larger and more sophisticated experimental
demonstrations. In particular, I am interested in exploring extensions to the language which enrich
the "classical/quantum" interface with ideas from distributed computing (such as message passing
interfaces or refinements to the OpenQASM memory model). I am also very interested in the
relationship between OpenQASM as a circuit representation to the next-generation of QEC tooling, for
which it may be natural to express experiments in other terms (e.g. with lattice surgery
operations). Along these frontiers and others, I will work to ensure that OpenQASM remains a pillar
of the industry.

## Jialin Dou (Quantinuum)

Quantinuum is the world’s largest integrated quantum computing company. Quantinuum focuses on
trapped-ion computing using the QCCD architecture. In addition to its high fidelity, the
architecture also allows for mid-circuit measurement.

As the Software Development Manager at Quantinuum, Jialin is responsible for the system software
teams, encompassing the compiler team, cloud platform team, and quantum programming language
team. Furthermore, Jialin assumes the role of Program Manager for Quantinuum's quantum chemistry
team.

Jialin's participation in the TSC would enable him to bring Quantinuum's unique perspectives.

## Simon Cross (Zurich Instruments)

Simon learned to code from the GW-BASIC manuals in the small town of
Melkbosstrand on the shores of the Atlantic.

Now by day he develops for Zurich Instruments, where he works on LabOne Q, their
open source experiment design and compiler toolkit. By night he is a QuTiP
maintainer, looking after its internal data structures and open quantum system
solvers, and fixing bugs and doing community support.

On the TSC, Simon hopes to represent two different communities of which
Zurich Instruments and QuTiP form a part:

- builders of current NISQ devices across a variety of quantum device
  architectures who are looking to incorporate OpenQASM as part of their control
  software or compilation chain today.

- authors of tools for simulating, modeling and optimizing quantum circuits at
  the pulse level, who are looking to use OpenQASM to describe the the
  circuit or control operations being modelled.

Simon has been indirectly involved with OpenQASM for some time: He helps maintain
QuTiP's OpenQASM 2 compiler, spends much of his time at Zurich Instruments
improving LabOne Q's OpenQASM 3 compiler, and supervised a student project at
Maastricht University to implement an OpenQASM 3 compiler for neutral atoms.

Recently he has made a few small contributions to OpenQASM itself, filing off
some rough edges in documentation and the handling of whitespace in duration
literals.

He is a big fan of the concept of "just-enough" governance and hopes to work
with the other members of the TSC to shepherd OpenQASM and OpenPulse from their
solid foundations to being mature specifications -- with excellent documentation
for implementers and coders, and a carefully selected set of software tooling to
help both produce excellent software.

Simon has a long history of contributing to the Python open source ecosystem,
and a PSF Community Service Award. He hopes to bring this experience to OpenQASM
and, in this way, continue being of service into the future.

## Yunong Shi (Amazon)

Yunong is a senior scientist driving the compilation effort at Amazon Braket. He helped introduce
OpenQASM3 into Braket, establishing it as the language specification for all gate-based
workloads. As one of the top contributors in the OpenQASM repository, he implemented the official
Python AST and has been an active participant in several working groups. Yunong’s research interests
mostly focus on breaking abstraction layers in the quantum software stack for better efficiency and
using formal methods to verify the correctness of quantum programs. With his research background,
Yunong has also made contributions to many open-source quantum compilers, including Qiskit, ScaffCC,
and a formally verified compiler, Giallar. If elected, Yunong aims to leverage his research
experience, his understanding of practical user demands for OpenQASM and his hands-on experience
with a variety of quantum technologies at Braket to help with the future evolution of OpenQASM,
ensuring it remains comprehensive, robust, and reflective of the community's needs.
