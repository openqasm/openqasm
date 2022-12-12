# Nominations for the TSC 2022-12-02

This document contains the nomination statements for each of the candidates for the TSC term of 2023/24.

[The electoral roll for this election](https://github.com/openqasm/openqasm/blob/tsc-election/2022-12-09/contributors.md) can be found in the previous link, or in the `contributors.md` file in the root of the repository as of the `tsc-election/2022-12-09` tag.

The election will take place online using the [Belenios online voting platform](https://www.belenios.org/).
Three people will be elected, to join Steven Heidel (Amazon), Bettina Heim (Nvidia) and Philipp Schindler (University of Innsbruck) whose seats are not up for re-election this cycle.
Votes will be counted using the [Condorcet/Schulze method](https://en.wikipedia.org/wiki/Schulze_method) to produce a ranked list of the candidates.
The top three candidates will be elected to the TSC.
The election will close on Friday the 13th of January, 2023 at 12:00 UTC.

In alphabetical order, the candidates are:

## Blake Johnson (IBM)

Blake is the Quantum Engine Lead at IBM Quantum, where one of his principal responsibilities is
technical evolution of what is executable on IBM Quantum systems. Blake has sought to ensure that
OpenQASM lives up to its name of being an open project, by soliciting feedback on early drafts of
the OpenQASM 3 proposal, and eventually forming the OpenQASM Technical Steering committee. If
elected for another term, Blake will strive to continue to expand the OpenQASM community and create
an ecosystem of people and code that work together across a variety of contexts (e.g. academic and
industry, qubit modality, etc.) while also pushing for a language that can exercise increasingly
powerful capabilities in quantum computing systems.


## Dor Israeli (Quantum Machines)

Dor is the Director of Software Strategy at Quantum Machines, one of the leading quantum control companies, and has vast experience in research, development, and managing complex projects with many partners. At Quantum Machines, Dor worked on their pulse-level programming language QUA, its compiler and algorithms, and its support for OpenQASM3. Moreover, he is the head of technology at the Israeli Quantum Computing Center. He is interested in the academic aspect of languages and their practical assimilation to the community stack (e.g., toolchains, compiler, HPC stack, and more). Dor has an M.Sc. in computer science (TAU) and B.Sc. in computer science and physics (HUJI).

In the last year, Dor has contributed to the OQ3 TSC on several issues and led and took part in a few working groups. His contributions rely on his expertise and insights from working on the physical, lower level of the stack, i.e., control of QM's customers' variety of physical qubits. QM has leading dynamic capabilities and performances (e.g., real-time variables, advanced arithmetic, control flow, and communication). Thus, Dor can help distill and define what will push the community forward and the implications on control vendors, as he presented at major conferences (e.g., APS22 presentation, QBE22 presentation, SQA22 abstract, and more).

## Florian Preis (Quantum Brilliance)

Florian is the Head of Software and Applications at Quantum Brilliance (QB).
QB is the leading company building room-temperature Quantum Accelerators based on nitrogen-vacancy centers in diamond.
Small room-temperature Quantum Accelerators offer the unique opportunity for massive parallelization or quantum computing at the edge.

Florian's team develops software that aims to support that vision by incorporating MPI, threading and GPU offload into the hybrid quantum-classical programming model.
The QB Software Development Kit (SDK) currently supports OpenQASM 2.0 and is looking forward to adopting OpenQASM 3.0.
Room-temperature Quantum Accelerators allow a close and therefore tight coupling to classical computers.
Thus, Florian will contribute to the OpenQASM community in pushing the OpenQASM 3 language forward to take full advantage of the real-time interaction between these two domains.
With Florian an additional quantum hardware platform will be represented on the TSC.


## Kartik Singhal (University of Chicago)

Kartik is a soon-to-graduate PhD candidate in programming languages at UChicago. He focuses on the design & semantics of quantum programming languages and the verification of quantum programs. He wrote and still maintains an [OCaml-based parser](https://opam.ocaml.org/packages/openQASM/) for OpenQASM 2.0 and worked on [translating it](https://ks.cs.uchicago.edu/publication/verified-translation/) to sQIR (a small quantum IR). In more recent work, he provided [formal semantics for Q#](https://ks.cs.uchicago.edu/publication/q-algol/) and suggested ways to improve its type system so that quantum programs do not fail at run time. Subtle design issues, such as uncontrolled aliasing, are not specific to Q# but also affect OpenQASM 3.x and other quantum languages lacking linear typing. His expertise in type systems and programming languages could help evolve OpenQASM into a safer common interface for current and future quantum hardware. Homepage: [ks.cs.uchicago.edu](https://ks.cs.uchicago.edu)

## Lev Bishop (IBM)

Lev leads the quantum software architecture team at IBM Quantum and has been involved with OpenQASM since the very beginning, before it was "Open" and was merely an internal project. His main technical goals have been to expand scope and adoption of the language while keeping a focus on making sure all the features are well-defined and work together properly so the language remains a tight interchange format and doesn't accidentally become a "kitchen-sink" language that by trying to please everyone ends up ill-suited to any particular task, nor becomes fragmented by incompatible partial implementations. If re-elected he intends to continue in this role of making sure all proposed additions have clear use-cases and interact cleanly with existing functionality. As recent examples of this approach please see the discussions around arrays (which were added to the language in a different form than the initial proposall) and dynamic qubit dereferencing (which was put on hold pending further language evolution). From a governance point of view Lev's philosophy is to introduce "just-enough" governance to allow smooth collaboration, which means only adding formality and process when there is a present need based on the size and tensions of the collaboration and otherwise keeping fast and lightweight. He thinks this approach has been successful so far for OpenQASM and is pleased with the evolution of the community during his first term, and if re-elected intends to use his TSC authority light-handedly with consensus as being the primary goal. An example of this approach was starting the initial openqasm repo within the qiskit org for expediency, but migrating to a dedicated org as soon as it became clear that there were advantages to doing so.

## Seyon Sivarajah (Quantinuum)
Seyon is technical lead in the Quantinuum systems software team, and is one of the primary developers of the
open source quantum compilation tool TKET. He also works on cloud orchestration tooling at Quantinuum.
Having worked on TKET's front-end support for OpenQASM2.0, and been the maintainer of TKET's Qiskit integration, 
Seyon is well positioned to provide compiler-level feedback to the OpenQASM 3.x Technical Steering Committee,
as well as providing input from the wider quantum software ecosystem. Seyon is also working on the
next generation of TKET, the design of which is motivated by many of the factors that motivate OpenQASM 3's
design (e.g. dynamic circuits, real-time classical logic) and so is interested in co-development of language and compiler.
