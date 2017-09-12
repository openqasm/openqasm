# Contributing

**We appreciate all kinds of help, so thank you!** :clap: :kissing_heart:

You can contribute in many ways to this project.

## Issue reporting

:fire: This is a good point to start, when you find a problem please add it to the [issue traker](https://github.com/IBMResearch/openqasm/issues). Please, use [this template](https://github.com/IBMResearch/contributing/blob/master/templates/issue.md) to add them.

## Doubts solving

:two_women_holding_hands: To help less advanced users is another wonderful way to start. You can help us to close some opened issues. This kind of tickets should be labeled as `question`.

## Improvement proposal

:smiling_imp: If you have an idea for a new feature please open a ticket labeled as `enhancement`. If you could also add a piece of code with the idea or a partial implementation it would be awesome.

## Documentation

:eyes: We all know the doc always need fixes/upgrades :wink:, so please feel free to send a PR (see next point) with what you found.

## Code

:star: This section include some tips that will help you to push source code.

### Commits

Please follow the next rules for the commit messages:

* It should be formed by a one-line subject, followed by one line of white space. Followed by one or more descriptive paragraphs, each separated by one line of white space. All of them finished by a dot.
* If it fixes an issue, it should include a reference to the issue ID in the first line of the commit.
* It should provide enough information for a reviewer to understand the changes and their relation to the rest of the code.

### Pull requests

* We use [GitHub pull requests](https://help.github.com/articles/about-pull-requests) to accept the contributions.
* Except for proposals (see next point), please, use [this template](https://github.com/IBMResearch/contributing/blob/master/templates/pr.md) to add them :smile:.
* Review the parts of the documentation regarding the new changes and update it if it's needed.
* New features often imply changes in the existent tests or new ones are needed. Once they're updated/added please be sure they keep passing.

## Spec proposals

:bulb: All new ideas go throught next stages to become a new feature of the language.

* Draft: Backlog items with different level of abstraction. Anybody can add one issue in the [main repo](https://github.ibm.com/IBMResearch/openqasm). Please label it as `draft`.
* Proposal: An idea with the correct form:
  * Add one issue in the [main repo](https://github.ibm.com/IBMResearch/openqasm) labeled as `proposal` using [this template](templates/proposal.md).
* Candidate: During each monthly meeting the assistants select the ones considered more interesting to pass to the next stage. One of the core devs will start commenting the issue to guide the owner into the next steps, including:
  * Fork [the main repo](https://github.ibm.com/IBMResearch/openqasm).
  * Add the content of the proposal, note that conformance tests are mandatory at this point.
  * Make a pull request.
  * The core dev can ask for changes before reaching the next stage.
* Accepted: When the PR is merged into master.

## Tests

The official [conformance tests](https://en.wikipedia.org/wiki/Conformance_testing) suite is located under the [test](test) folder.

For convenience this project uses the [QISKit](https://github.com/QISKit/qiskit-sdk-py) parser.

The test runner uses all the circuit files in the [examples](examples) folder. They are run automatically to check they keep passing the parser. It allows to drop more files in those folders, even to add new ones.

* The `invalid` folder includes circuits which should raise a `QasmException`.
* The rest include valid circuits.
* Optionally, they can include metadata in the header (inside comments, like [this one](examples/invalid/gate_no_found.qasm)):
  * name: Descriptive name for the check this example is covering.
  * section: Link to the related part of the specification.

### Run

* Install [QISKit depedencies](https://github.com/QISKit/qiskit-sdk-py#1-get-the-tools).
* The command `make test` should finish without errors communicate with the reviewer using the issue comments to show that we're done.

## Versions

:watch: Due to the fast-changing nature of the quantum computing environment the idea is provide a new version of the specification per year, over June. The previous monthly meetings should include the next tasks:

* April: All the accepted proposals (already merged to `develop`) are re-confirmed by the assistants. The dev team have this month to resolve possible conflicts here.
* May: From here, the unique accepted commits will be editorial ones.
* June:
  * Merge of `develop` into `master`, drop the branch and create a tag with this the new version name.
  * The new standard is considered approved and must be published to the communities. A new human-readable version should be placed into the [spec-human] folder. The file must include this version number, ie: `qasm2.pdf`.