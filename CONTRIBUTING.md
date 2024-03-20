Table of Contents
=================

* [Contributing](#contributing)
   * [Issue reporting](#issue-reporting)
   * [Doubts solving](#doubts-solving)
   * [Improvement proposal](#improvement-proposal)
   * [Documentation](#documentation)
   * [Code](#code)
      * [Commits](#commits)
      * [Pull requests](#pull-requests)
   * [Spec proposals](#spec-proposals)
   * [Development Cycle](#development-cycle)
      * [Semantic Versioning](#semantic-versioning)
      * [Branches](#branches)
      * [Release Notes](#release-notes)
         * [Adding a new release note](#adding-a-new-release-note)
      * [Tags](#tags)
      * [Release cycle](#release-cycle)
         * [Example release cycle](#example-release-cycle)

# Contributing

**We appreciate all kinds of help, so thank you!** :clap: :kissing_heart:

You can contribute in many ways to this project.

## Issue reporting

:fire: This is a good point to start, when you find a problem please add it to the [issue tracker](https://github.com/openqasm/openqasm/issues).

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
- Except for proposals (see next point), please, use [pull requests](https://github.com/openqasm/openqasm/pulls) as is to submit a new one :smile:.
- Review the parts of the documentation regarding the new changes and update it if it's needed.
- New features often imply changes in the existent tests or new ones are needed. Once they're updated/added please be sure they keep passing.

## Spec proposals

:bulb: All new ideas go through the following stages to become a new feature of the language:

- Draft: Backlog items with different levels of abstraction. Anybody can add an issue in the [main repo](https://github.com/openqasm/openqasm). Please label it as `draft`.
- Proposal: An idea with the correct form:
  - Add an issue in the [main repo](https://github.com/openqasm/openqasm) labeled as `proposal` using [the spec proposal template](https://github.com/openqasm/openqasm/issues/new?template=spec_proposal.yaml)
- Candidate: During each monthly meeting the assistants select the ones considered more interesting to pass to the next stage. One of the core devs will start commenting on the issue to guide the owner into the next steps, including:
  - Fork [the main repo](https://github.com/openqasm/openqasm).
  - Add the content of the proposal, note that conformance tests are mandatory at this point.
  - Make a pull request.
  - The core dev can ask for changes before reaching the next stage.
- Accepted: When the PR is merged into main.

## Development Cycle

The development cycle for OpenQASM is managed in the open using Github for project management.
Release notes are collected separately for the specification and reference parser in
the `releasenotes` directory.

### Semantic Versioning
The OpenQASM language uses [semantic versioning (semver)](https://semver.org/).
All official releases are identified by a valid semver (See [Tags](#tags)).
The latest development branch (See [Branches](#branches)) is always identified
by the semver `<next_major>.<next_minor>.0-dev` where `next_<major/minor>` are
the target major/minor versions of the next release. Specification changes that
require backwards incompatible changes to most parsers generally will warrant
a major version increase, while less drastic changes only warrant a minor
version increase.

### Timing of Releases

The OpenQASM Technical Steering Committee is the final arbiter on when a new
semantic version of the specification and reference parser is warranted. The TSC
expects the cadence of releases to be dicated by the contributions provided by
the community, and not by a time-based schedule.

### Branches

* `main`:
The main branch is used for the development of the next OpenQASM release.
It is updated frequently and should not be considered stable. On the development
branch, the language specification can and will change (possible breaking)
as new language features are introduced and refined.
All efforts should be made to ensure that the development branch is maintained in
a self-consistent state that is passing continuous integration (CI).
Changes should not be merged unless they are verified by CI. The latest
development specification of the language (called the live spec) is automatically
[published by CI](https://openqasm.github.io/) for easy access to the current development HEAD.
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

### Release Notes

When making any end user facing changes in a contribution we have to make sure
we document that when we release a new version of OpenQASM. The expectation
is that if your code contribution has user facing changes that you will write
the release documentation for these changes. This documentation must explain
what was changed, why it was changed, and how users can either use or adapt
to the change. The idea behind release documentation is that when a naive
user with limited internal knowledge of the project is upgrading from the
previous release to the new one, they should be able to read the release notes,
understand if they need to update their project which uses OpenQASM, and how they
would go about doing that. It ideally should explain why they need to make
this change too, to provide the necessary context.

To make sure we don't forget a release note or if the details of user facing
changes over a release cycle we require that all user facing changes include
documentation at the same time as the code. To accomplish this we use the
[reno](https://docs.openstack.org/reno/latest/) tool which enables a Git-based
workflow for writing and compiling release notes.

Release notes are separated for updates to the specification and the
grammar/ast generator. The specification release notes are in `spec_releasenotes`
and the ast/grammar release notes are in `ast_releasenotes`.

#### Adding a new release note

Making a new release note is quite straightforward. Ensure that you have reno
installed with::

    pip install -U reno

Once you have reno installed you can make a new release note by running in
your local repository checkout's spec or ast releasenotes dir::

    reno new short-description-string

where short-description-string is a brief string (with no spaces) that describes
what's in the release note. This will become the prefix for the release note
file. Once that is run it will create a new yaml file in releasenotes/notes.
Then open that yaml file in a text editor and write the release note. The basic
structure of a release note is restructured text in yaml lists under category
keys. You add individual items under each category and they will be grouped
automatically by release when the release notes are compiled. A single file
can have as many entries in it as needed, but to avoid potential conflicts
you'll want to create a new file for each pull request that has user facing
changes. When you open the newly created file it will be a full template of
the different categories with a description of a category as a single entry
in each category. You'll want to delete all the sections you aren't using and
update the contents for those you are. For example, the end result should
look something like::

```yaml
features:
  - |
    Introduced a new ``pragma fabulizer`` that adds support for new compiler technology
    for ``defcal``s. For example::

      pragma defcal_fabulizer
      defcal reset $0 {
      ...

  - |
    The ``defcal`` fabulizer will fabulize your defcal.

deprecations:
  - |
    The ``pragma defcal_fromulizer`` has been deprecated and will be removed in a
    future release. Its sole function has been superseded by the fabulizer.

```

You can also look at other release notes for other examples.

You can use any restructured text feature in them (code sections, tables,
enumerated lists, bulleted list, etc) to express what is being changed as
needed. In general you want the release notes to include as much detail as
needed so that users will understand what has changed, why it changed, and how
they'll have to update their code.

After you've finished writing your release notes you'll want to add the note
file to your commit with `git add` and commit them to your PR branch to make
sure they're included with the code in your PR.

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
