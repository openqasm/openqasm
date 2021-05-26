# OpenQASM Governance model

## Purpose

The purpose of the OpenQASM governance model is to formalize the process for proposing and deciding upon changes to OpenQASM. It provides explicit mechanisms for a broader community to contribute. It will memorialize decisions in a public record. This model should make decision-making routine to get issues unstuck.

OpenQASM is a Qiskit project, but this governance structure is scoped to just OpenQASM itself and not Qiskit as a whole. The scope of OpenQASM includes the language specification as well as reference implementations of parsers or other low-level infrastructure to facilitate use in other projects.

**In brief**: we propose 3 community roles: **Member**, **Contributor**, and **TSC Member**. We also propose 2 structures: a **Technical Steering Committee** (TSC) and **Working Group** (WG). The TSC creates WGs and appoints WG chairs. Working Group membership shall be composed of Members with a Contributor as chair.

## Roles

**Member** - individuals that participate in the OpenQASM project and community. These people must adhere to the Qiskit Code of Conduct but have no specific further responsibilities.

**Contributor** - a **Member** who is an active contributor to the OpenQASM community. This person has a *sustained history* of authoring, commenting on, and reviewing issues and PRs. They post questions or responses to the community Slack (#open-qasm in the Qiskit workspace). Contributors are selected by nomination of at least 2 current TSC Members. *Contributors may participate in WGs and attend TSC meetings.*

**TSC Member** - a **Contributor** who also regularly attends and has voting rights at Technical Steering Committee meetings.

## Structures

We will form a **Technical Steering Committee**. The TSC shall be composed of 5 Contributors. The initial TSC will include:
* Ali Javadi (IBM Quantum)
* Lev S Bishop (IBM Quantum)
* Blake Johnson (IBM Quantum)
* Steven Heidel (AWS)
* TBD (another non-IBM member, to be selected by the TSC)

TSC meetings shall be open to all **Contributors**. The TSC will make decisions by simple majority vote of its members. TSC meetings shall require a quorum of 60% of voting members present to make a decision by vote (ie, 3 members for the initial TSC). If a TSC meeting does not have quorum, it may still discuss and record minutes. The TSC may make decisions outside of meetings (e.g. on a pull request) so long as voting/approval in that forum meets the quorum requirement. Upon request from any TSC member, any decision must be deferred until the next TSC meeting, to enable live discussion.

The TSC responsibility is to balance a desire to allow a voice to the broad OpenQASM community; with lightweight processes to enable moving fast and maintaining a consistent philosophy for the language. Thus, for example, this governance document does give the freedom to the TSC to make decisions without calling a meeting and explicitly involving contributors, but the idea is that the TSC should make use of this power judiciously. The TSC has authority to make all decisions regarding OpenQASM (including amendments to this governance document), but should apply more process and seek more community input on constitutional changes than for simple fixes to the spec.

The TSC may have a **Secretary** (non-voting **Contributor**) who organizes the meeting (e.g. prepares and distributes the agenda and collects a set of issues to be considered). The TSC **Secretary** will be appointed by vote of the TSC.
* Zach Schoenfeld (IBM Quantum) is nominated to serve as the first TSC **Secretary**.

The TSC will, from time to time, elect to create **Working Groups** to study issues. The TSC will appoint a **Contributor** as chair for each WG. These WGs should come back to the TSC with a proposal in the form of a language RFC or pull request to the OpenQASM specification. A WG will be automatically disbanded upon acceptance or (final) rejection of an RFC. A potential set of initial Working Groups might include:
* Pulse grammar
* Types and casting (including implicit casts)
* Generics, circuit families, and subroutines
* Defcal for non-unitaries

## Open Questions

* How will new **TSC Members** be selected when current **TSC Members** step down?
    - Suggestion: nomination power to reside with TSC, voting open to all **Contributors**
* Do we need term limits? The various source models we considered typically use a 2 year term.
* Do we also need "special interest groups" (see any of the reference models)? My feeling is that Working Groups are probably sufficient at this stage.


### Reference models

* [Kubernetes](https://github.com/kubernetes/community/blob/master/governance.md)
    - See also their [Special Interest Group governance rules](https://github.com/kubernetes/community/blob/master/committee-steering/governance/sig-governance.md)
* [Cloud Native Foundation](https://github.com/cncf/foundation/blob/master/charter.md)
* [ONNX](https://github.com/onnx/onnx/tree/master/community)
