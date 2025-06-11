.. _sec:profiles:

Things to consider while writing profiles
=========================================



Profiles
========

Define a minimum set of features for hardware implementors (basic profile) and a framework for structuring additional profiles.

Description: One of the core tenets of OpenQASM 3.0 is versatility, and in particular the idea that not all hardware and tooling needs to support all OpenQASM 3.0 features. A hardware implementor can assume that certain aspects of compilation are dealt with at a higher-level, and can focus their implementation on only core features of the language.https://github.com/qir-alliance/qir-spec/tree/main/specification/under_development/profiles

https://github.com/qir-alliance/qir-spec/blob/main/specification/under_development/profiles/Base_Profile.md

https://github.com/qir-alliance/qir-spec/blob/main/specification/under_development/profiles/Adaptive_Profile.md

.. toctree::

   base
   adaptive


Make profiles for both OpenQASM and OpenPulse.

Profile sources of ideas:

- limiting scope of language (simplify things for compilers)
- make a list of what is hard for hardware
- or hard for simulators
- OpenQASM 2 conceptual profile
- restricting types

- make some opionated pushes
- provoke healthy disagreement

- make PR with basic structure
- ask Stephen to change permissions
- write minutes
  - Present: Erik Davis, Blake Johnson, Simon Cross
  - Apologies: Jialin Dou

Erik Davis:

- Used to use Python language.
- Move to OpenQASM for a few reasons:
  - Why re-develop all the classical logic.
