# OpenQASM Governance model

## Purpose

The purpose of the OpenQASM governance model is to formalize the process for proposing and deciding upon changes to OpenQASM. It provides explicit mechanisms for a broader community to contribute. It will memorialize decisions in a public record. This model should make decision-making routine to get issues unstuck.

This governance structure is scoped to just OpenQASM itself and not Qiskit as a whole. The scope of OpenQASM includes the language specification as well as reference implementations of parsers or other low-level infrastructure to facilitate use in other projects. OpenQASM inherits the contribution guidelines and community standards that are common to all projects within the Qiskit GitHub organization.

**In brief**: we propose 3 community roles: **Member**, **Contributor**, and **TSC Member**. We also propose 2 structures: a **Technical Steering Committee** (TSC) and **Working Group** (WG). The TSC creates WGs and appoints WG chairs. Working Group membership shall be composed of Members with a Contributor as chair.

## Roles

**Member** - individuals that participate in the OpenQASM project and community. These people must adhere to the Qiskit Code of Conduct but have no specific further responsibilities.

**Contributor** - a **Member** who is an active contributor to the OpenQASM community. This person has a *sustained history* of authoring, commenting on, and reviewing issues and PRs. They post questions or responses to the community Slack (#open-qasm in the Qiskit workspace). Contributors are selected by nomination of at least 2 current TSC Members. *Contributors may participate in WGs and attend TSC meetings, but do not vote.* **Contributors** will be given commit access to the OpenQASM repository. **Contributor** status may be revoked at the discretion of the TSC.

**TSC Member** - a **Contributor** who also regularly attends and has voting rights at Technical Steering Committee meetings.

## Structures

We will form a **Technical Steering Committee**. The TSC shall be composed of 6 Contributors. The current TSC is:

* Dor Israeli (Quantum Machines)
* Lev S Bishop (IBM Quantum)
* Blake Johnson (IBM Quantum)
* Erik Davis (AWS)
* Bettina Heim (Nvidia)
* Philipp Schindler (Innsbruck)

TSC meetings shall be open to all **Contributors**. The TSC may invite additional guests at its discretion. The TSC will make decisions by simple majority vote of its members. TSC meetings shall require a quorum of 66% of voting members present to make a decision by vote (ie, 4 members for the initial TSC). If a TSC meeting does not have quorum, it may still discuss and record minutes. The TSC may make decisions outside of meetings (e.g. on a pull request) so long as voting/approval in that forum meets the quorum requirement. Upon request from any TSC member, any decision must be deferred until the next TSC meeting, to enable live discussion.

The TSC responsibility is to balance a desire to allow a voice to the broad OpenQASM community with lightweight processes to enable moving fast and maintaining a consistent philosophy for the language. Thus, for example, this governance document does give the freedom to the TSC to make decisions without calling a meeting and explicitly involving contributors, but the idea is that the TSC should make use of this power judiciously. The TSC aims to build consensus among **Contributors** prior to voting in most cases. Voting to resolve disagreements is ideally expected to happen less often than voting to accept the consensus. The TSC has authority to make all decisions regarding OpenQASM (including amendments to this governance document), but should apply more process and seek more community input on constitutional changes than for simple fixes to the language specification.

The TSC may have a **Secretary**  who organizes the meeting. The TSC **Secretary** will be a **Contributor** appointed by vote of the TSC. The appointment term is for 6 months and renewable.
The responsibility of the TSC **Secretary** include:

* Schedule and host the TSC meetings
* Keep minutes for the TSC meetings
* Keep track on stalled issues and PRs and raise them to the TSC for attention (either in the Slack channel or as part of the TSC meeting)
* Independently recognize controversy and conflicting ideas and make agenda items for them
* Maintain and manage the contributors access privileges in the repository, Slack channels, meeting invites, etc.
* Maintain general documents such as `WG.md`

The TSC will, from time to time, elect to create **Working Groups** to study issues. The TSC will appoint a **Contributor** as chair for each WG. These WGs should come back to the TSC with a proposal in the form of a language RFC or pull request to the OpenQASM specification. A WG will be automatically disbanded upon acceptance or (final) rejection of an RFC.

**TSC Members** will serve a 2-year term, with the exception of the founding TSC which will have staggered terms to avoid an election of an entire TSC all at once. New **TSC Members** will be selected by nomination of the TSC, followed by a vote which is open to all **Contributors**. Outgoing **TSC Members** participate in the nomination process which selects their successors. Note that **TSC Members** may be re-elected to serve additional 2-year terms. The same process will be used in the event that a **TSC Member** resigns prior to the end of their term. The TSC may also appoint an individual to fulfill the balance of a resigning **TSC Member's** term.


### Past TSCs

* On 2023-06-13, Steven Heidel resigned and the TSC appointed Erik Davis (AWS) to serve the remainder of Steven's term.

* The initial TSC, finishing on 2023-01-13 was:

  - Ali Javadi (IBM Quantum)
  - Lev S Bishop (IBM Quantum)
  - Blake Johnson (IBM Quantum)
  - Steven Heidel (AWS)
  - Bettina Heim (Nvidia)
  - Philipp Schindler (Innsbruck)

  This TSC was completed by an election ending on 2023-01-13 to elect the seats held by Ali, Lev and Blake.  Ali chose not to stand again.  The other three seats were chosen to have staggered terms, with their election due to start at the end of 2023.


### Reference models

* [Kubernetes](https://github.com/kubernetes/community/blob/master/governance.md)
    - See also their [Special Interest Group governance rules](https://github.com/kubernetes/community/blob/master/committee-steering/governance/sig-governance.md)
* [Cloud Native Foundation](https://github.com/cncf/foundation/blob/master/charter.md)
* [ONNX](https://github.com/onnx/onnx/tree/master/community)
