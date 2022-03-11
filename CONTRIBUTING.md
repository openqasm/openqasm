# Contributing

**We appreciate all kinds of help, so thank you!** :clap: :kissing_heart:

You can contribute in many ways to this project.

## Issue reporting

:fire: This is a good point to start, when you find a problem please add it to the [issue tracker](https://github.com/Qiskit/openqasm/issues). Please, use [this template](https://github.com/Qiskit/openqasm/contributing/blob/main/templates/issue.md) to add them.

## Doubts solving

:two_women_holding_hands: To help less advanced users is another wonderful way to start. You can help us to close some open issues. This kind of ticket should be labeled with `question`.

## Improvement proposal

:smiling_imp: If you have an idea for a new feature please open a ticket labeled as `enhancement`. If you could also add a piece of code with the idea or a partial implementation it would be awesome.

## Documentation

:eyes: We all know the doc always needs fixes/upgrades :wink:, so please feel free to send a PR (see next point) with what you found.

## Code

:star: This section includes some tips that will help you to push source code.

### Commits

Please follow the next rules for the commit messages:

- It should be formed by a one-line subject, followed by one line of white space. Followed by one or more descriptive paragraphs, each separated by one line of white space. All of them finished by a dot.
- If it fixes an issue, it should include a reference to the issue ID in the first line of the commit.
- It should provide enough information for a reviewer to understand the changes and their relation to the rest of the code.

### Pull requests

- We use [GitHub pull requests](https://help.github.com/articles/about-pull-requests) to accept the contributions.
- Except for proposals (see next point), please, use [pull requests](https://github.com/Qiskit/openqasm/pulls) as is to submit a new one :smile:.
- Review the parts of the documentation regarding the new changes and update it if it's needed.
- New features often imply changes in the existent tests or new ones are needed. Once they're updated/added please be sure they keep passing.

## Spec proposals

:bulb: All new ideas go through the next stages to become a new feature of the language.

- Draft: Backlog items with different levels of abstraction. Anybody can add one issue in the [main repo](https://github.com/Qiskit/openqasm). Please label it as `draft`.
- Proposal: An idea with the correct form:
  - Add one issue in the [main repo](https://github.com/Qiskit/openqasm) labeled as `proposal` using [this template](templates/proposal.md).
- Candidate: During each monthly meeting the assistants select the ones considered more interesting to pass to the next stage. One of the core devs will start commenting on the issue to guide the owner into the next steps, including:
  - Fork [the main repo](https://github.com/Qiskit/openqasm).
  - Add the content of the proposal, note that conformance tests are mandatory at this point.
  - Make a pull request.
  - The core dev can ask for changes before reaching the next stage.
- Accepted: When the PR is merged into main.

## Tests

The official [conformance tests](https://en.wikipedia.org/wiki/Conformance_testing) suite is located under the [test](test) folder.

For convenience, this project uses the [Qiskit](https://github.com/Qiskit/qiskit-terra) parser.

The test runner uses all the circuit files in the [examples](examples) folder. They are run automatically to check they keep passing the parser. It allows dropping more files in those folders, even adding new ones.

- The `invalid` folder includes circuits that should raise a `QasmException`.
- The rest include valid circuits.
- Optionally, they can include metadata in the header (inside comments, like [this one](examples/invalid/gate_no_found.qasm)):
  - name: Descriptive name for the check this example is covering.
  - section: Link to the related part of the specification.

### Run

- Install [Qiskit dependencies](https://github.com/Qiskit/qiskit-terra#installation).
- The command `make test` should finish without errors communicate with the reviewer using the issue comments to show that we're done.


## Development Cycle

The development cycle for OpenQASM is managed in the open using Github for project management.
TODO: When preparing a new release changes for the released version should be identified
in the release notes (See [issue #328](https://github.com/Qiskit/openqasm/issues/328)).

### Semantic Versioning
The OpenQASM language uses [semantic versioning (semver)](https://semver.org/).
All official releases are identified by a valid semver (See [Tags](#tags)).
The latest development branch (See [Branches](#branches)) is always identified
by the semver `<next_major>.<next_minor>.0-dev` where `next_<major/minor>` are
the target major/minor versions of the next release.

### Branches

* `main`:
The main branch is used for the development of the next OpenQASM release.
It is updated frequently and should not be considered stable. On the development
branch, the language specification can and will change (possible breaking)
as new language features are introduced and refined.
All efforts should be made to ensure that the development branch is maintained in
a self-consistent state that is passing continuous integration (CI).
Changes should not be merged unless they are verified by CI. TODO: The latest
development specification of the language should be automatically published by CI
to a fixed URL for easy access to the current development HEAD.
* `stable/<major.minor>` branches:
Branches under `stable/<major.minor>` are used to maintain released versions of the OpenQASM
specification. They contain the version of the specification corresponding to the
release as identified by its [semantic version](https://semver.org/). For example,
stable/3.2 would be the specification version for major version 3
(corresponding to OpenQASM3) and minor version 2. On these branches, the language specification
is considered stable. The only changes that may be merged to a stable branch are
patches/bugfixes. When a patch is required when possible the fix should
first be made to the development branch through a pull request.
The fix should then be backported from the development branch to the
target stable branch (of name `stable/<major.minor>`) by creating a pull request on
Github into the target stable branch with the relevant cherry-picked commits.
The new stable branch `HEAD` should be tagged (see [Tags](#tags)) with a new
`<major.minor.patch>` version and pushed to Github.

### Tags
Git tags are used to tag the specific commit associated with a versioned release.
Tags must take the form of `<major>.<minor>.<patch>-<labels>`. For example the semver
`3.2.1` would point to the language specification with major version 3 (OpenQASM 3),
minor version 2, and, patch version 1. The current development version would therefore be
`3.3.0-dev`. All official releases when tagged must always point to the current HEAD
of a stable branch. TODO: Tags are used to trigger CI to deploy and publish new releases
of the language specification.


### Release cycle

To release a version a new version of OpenQASM:

1. (optional) If releasing a minor version create a new stable branch for the minor version (See [Branches](#branches)).
   This should be cut from the latest development branch.
2.  Create a new tag with the required semantic version number (see [Tags](#tags)) and push it to Github which will trigger CI (TODO).
3.  Update the development branch version identifier to the next release version (`<major>.<minor+1>.0-dev`).
4.  TODO: Enable CI to create a Github release page with a generated changelog, publish documentation for the
    new version to Github pages, and update the root language specification URL to point to the latest release.

#### Example release cycle

For this example assume the current release of OpenQASM is version `3.1.1`. This will correspond to a commit
on `stable/3.1`. The project's development branch reflects the development state of the next release - `3.2.0`
and is referred to by version as `3.2.0-dev`.

To trigger a bugfix release - `3.1.2`:
1. Create a PR into `stable/3.1` with all required changes. These may be backported commits from `3.2.0-dev`.
2. Upon merger of the PR tag the HEAD of `stable/3.1` with `3.1.2` and push to Github.

To trigger a minor release - `3.2.0`:
1. Create a new stable branch `stable/3.2` using the current development branch as the base branch, eg., `git checkout -b stable/3.2 main`.
2. Push this branch to Github.
3. Tag the branch with `3.2.0` and push to Github.

