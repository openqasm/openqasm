# Technical Steering Commitee members' Statements of Intent

In alphabetical order

## Blake Johnson (IBM Quantum)

Blake is the Quantum Engine Lead at IBM Quantum, where one of his principal responsibilities is
technical evolution of what is executable on IBM Quantum systems. Blake has sought to ensure that
OpenQASM lives up to its name of being an open project, by soliciting feedback on early drafts of
the OpenQASM 3 proposal, and eventually forming the OpenQASM Technical Steering committee. If
elected for another term, Blake will strive to continue to expand the OpenQASM community and create
an ecosystem of people and code that work together across a variety of contexts (e.g. academic and
industry, qubit modality, etc.) while also pushing for a language that can exercise increasingly
powerful capabilities in quantum computing systems.

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

## Lev Bishop (IBM Quantum)

Lev leads the quantum software architecture team at IBM Quantum and has been involved with OpenQASM since the very beginning, before it was "Open" and was merely an internal project. His main technical goals have been to expand scope and adoption of the language while keeping a focus on making sure all the features are well-defined and work together properly so the language remains a tight interchange format and doesn't accidentally become a "kitchen-sink" language that by trying to please everyone ends up ill-suited to any particular task, nor becomes fragmented by incompatible partial implementations. If re-elected he intends to continue in this role of making sure all proposed additions have clear use-cases and interact cleanly with existing functionality. As recent examples of this approach please see the discussions around arrays (which were added to the language in a different form than the initial proposall) and dynamic qubit dereferencing (which was put on hold pending further language evolution). From a governance point of view Lev's philosophy is to introduce "just-enough" governance to allow smooth collaboration, which means only adding formality and process when there is a present need based on the size and tensions of the collaboration and otherwise keeping fast and lightweight. He thinks this approach has been successful so far for OpenQASM and is pleased with the evolution of the community during his first term, and if re-elected intends to use his TSC authority light-handedly with consensus as being the primary goal. An example of this approach was starting the initial openqasm repo within the qiskit org for expediency, but migrating to a dedicated org as soon as it became clear that there were advantages to doing so.


## Serwan Asaad (Quantum Machines)

Serwan Asaad is a product manager at Quantum Machines where he leads the development of software layers above the QUA pulse-level language, which include the calibration software QUAlibrate and the OpenQASM3-to-QUA compiler. He also developed the open-source software QuAM, which can effectively translate gates into hardware-specific pulse-level instructions, and thus facilitates OpenQASM3-to-QUA compilation.

Serwan holds a PhD from UNSW, where he demonstrated the coherent electric control of a high-spin nucleus and achieved record-breaking spin-qubit 2Q gate fidelities. Throughout his academic career, Serwan had a strong focus on developing measurement control software such as [SilQ](https://nulinspiratie.github.io/SilQ/) (not to be confused with Silq), and contributing to the open-source projects QCoDeS and PycQED.

Serwan predicts a transition towards circuit-level languages for quantum control, and OpenQASM3 serves as a necessary bridge in this transition. We're hearing requests from several partners and customers, and we want to promote this integration as much as possible. Ensuring its continued adoption as a standard requires tight collaboration with relevant parties both up and down the stack. Serwan can contribute to this by discussing the challenges and resolutions that arise when integrating OpenQASM3 with hardware-specific languages.

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
