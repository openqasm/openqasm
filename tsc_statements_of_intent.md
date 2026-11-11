# Technical Steering Commitee members' Statements of Intent

In alphabetical order

## Lev Bishop (IBM Quantum)

Lev leads the quantum software architecture team at IBM Quantum and has been involved with OpenQASM since the very beginning, before it was "Open" and was merely an internal project. His main technical goals have been to expand scope and adoption of the language while keeping a focus on making sure all the features are well-defined and work together properly so the language remains a tight interchange format and doesn't accidentally become a "kitchen-sink" language that by trying to please everyone ends up ill-suited to any particular task, nor becomes fragmented by incompatible partial implementations. If re-elected he intends to continue in this role of making sure all proposed additions have clear use-cases and interact cleanly with existing functionality. As recent examples of this approach please see the discussions around arrays (which were added to the language in a different form than the initial proposall) and dynamic qubit dereferencing (which was put on hold pending further language evolution). From a governance point of view Lev's philosophy is to introduce "just-enough" governance to allow smooth collaboration, which means only adding formality and process when there is a present need based on the size and tensions of the collaboration and otherwise keeping fast and lightweight. He thinks this approach has been successful so far for OpenQASM and is pleased with the evolution of the community during his first term, and if re-elected intends to use his TSC authority light-handedly with consensus as being the primary goal. An example of this approach was starting the initial openqasm repo within the qiskit org for expediency, but migrating to a dedicated org as soon as it became clear that there were advantages to doing so.

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

## Aniket Dalvi (Amazon Braket)

Amazon Braket provides users access to diverse quantum hardware hosted on AWS cloud infrastructure. As an Applied Scientist at Braket, I focus on quantum compilation and expanding OpenQASM 3 support across our hardware and simulator offerings. Prior to this, I earned my PhD at Duke University, where my research spanned the quantum stack with a focus on control software, compilation, and representations. As part of my research on Quantum Intermediate Representation, I extensively studied the evolution of OpenQASM and its role in the current software stack.

Throughout my career, I have utilized OpenQASM as both a primary input language and a critical interchange format for compiler optimization. My background bridges the gap between academic research and industrial-scale implementation, giving me a unique perspective on the requirements and utility of the language across different personas. With over 10 years of experience in the open-source community, I look forward to contributing toward the development and maintenance of OpenQASM.

We are at a pivotal juncture where NISQ and early fault-tolerant devices co-exist. If elected to the Steering Committee, I will work to ensure OpenQASM remains a stable, empowering standard for current users while proactively defining the language features necessary to transition us into the fault-tolerant era.

## Ian Davis (Microsoft)

I am a Principal Engineer working on quantum compilers, developer tooling, and ecosystem interoperability within the Microsoft Quantum Development Kit. My work has focused on language and compiler infrastructure, including the design and implementation of OpenQASM 2.0 and 3.0 parsing, semantic analysis, and compiler integration within the QDK, as well as OpenQASM language service capabilities in Visual Studio Code. I have also contributed to the broader quantum IR ecosystem as an author of PyQIR, co-author of qir-runner, and as a member of the QIR Alliance steering committee.

Through this work, I have developed a deep appreciation for the role OpenQASM plays as a common interchange format across quantum platforms, toolchains, and vendors. I actively participate in OpenQASM TSC meetings, contribute issues and reviews, and help evolve the language specification to reflect real-world compiler and tooling needs. My experience spans both specification design and production compiler implementations, giving me a pragmatic perspective on how language decisions affect interoperability, correctness, and long-term maintainability.

If selected to continue serving the OpenQASM community in a governance role, my goal would be to help ensure that OpenQASM remains a stable, extensible, and implementation-friendly foundation for the quantum ecosystem. I am interested in strengthening alignment between OpenQASM, intermediate representations such as QIR, and developer tooling, so that advances in one area translate cleanly and predictably across the stack. With over 18 years of open‑source experience, I am committed to transparent governance and sustaining OpenQASM as an open, cross‑vendor foundation for quantum software that enables innovation.

## Uri Goldblatt (Quantum Machines)

I am a Product Solutions Physicist at Quantum Machines. I am the technical lead for high-tier customers, turning their control requirements into solutions together with our product and R&D teams. I hold a Ph.D. in physics from the Weizmann Institute of Science, where I built superconducting cavity–transmon experiments end to end, from 3D cavity design and simulation through chip fabrication to cryogenic measurement. My main result used real-time feedback, meaning adaptive measurements with decisions made on the fly, to recover the coherence of a cavity qubit coupled to a noisy ancilla Goldblatt et al., Phys. Rev. X, 2024. Before that, I spent three years on Apple's FPGA prototyping and emulation team.

My interest in OpenQASM comes from my thesis work, where much of my time went into real-time feedback: measuring, deciding, and correcting while the experiment runs. Quantum Machines sees real value in OpenQASM 3 as a common standard in a field that still has few and supports it both by contributing to the language and by compiling it to QUA, our pulse-level language. If elected, I would bring this experimental perspective to the TSC and help ensure that real-time control in OpenQASM stays practical to write and straightforward to implement on control hardware.

## Blake Johnson (IBM Quantum)

Blake is the Quantum Engine Lead at IBM Quantum, where one of his principal responsibilities is
technical evolution of what is executable on IBM Quantum systems. Blake has sought to ensure that
OpenQASM lives up to its name of being an open project, by soliciting feedback on early drafts of
the OpenQASM 3 proposal, and eventually forming the OpenQASM Technical Steering committee. If
elected for another term, Blake will strive to continue to expand the OpenQASM community and create
an ecosystem of people and code that work together across a variety of contexts (e.g. academic and
industry, qubit modality, etc.) while also pushing for a language that can exercise increasingly
powerful capabilities in quantum computing systems.
