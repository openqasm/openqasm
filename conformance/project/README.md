---
title: OpenQASM project compatibility suite
description: Language-agnostic compatibility cases for the OpenQASM project definition
---

A language-agnostic corpus for the non-normative
[project definition](https://openqasm.com/project.html). It provides a shared
set of cases through which independent project-loader implementations written
in different languages can demonstrate that they agree.

## What is under test

Three different things, and a case says which.

| Class | Subject | Needs a parser? |
| --- | --- | --- |
| `loader` | Project discovery, file-set construction, canonical naming, containment, and mapping construction. | No |
| `parser` | The above, plus handing the loaded project environment to an OpenQASM parser and observing include resolution. | Yes |
| `derivation` | The above, plus parsing every project source to derive compilation roots when `programs` is absent. | Yes |

The loader only reads the project and returns its finite source inventory and
owner-local library bindings. It does not follow `include` statements. The
parser receives one environment that binds those together and performs include
resolution, so parser cases can test behavior such as incorporating a diamond
include once, diagnosing a cycle, or enforcing an inclusion-depth limit.
Derivation cases parse the finite project inventory to identify which project
sources no other project source includes.

An implementation that provides only a loader runs the `loader` cases and skips
the `parser` and `derivation` cases. That is a valid result and the runner
reports it as such.

## Layout

```text
conformance/project/
├── README.md            this file
├── harness.py           runs the corpus against any compatible runner
├── cases/               committed cases, one directory each
│   └── NN-name/
│       ├── case.json    metadata: class, subject file, expectation
│       └── project/     the input tree, used verbatim
├── generated/
│   └── generate.py      cases that cannot be committed as ordinary files
└── runners/
    └── python/          the reference runner, one per implementation
```

A case directory name is `NN-name`, where `name` says what the case tests. Each
case tests one thing, and a case expecting an error is named after the fault.

## Case metadata

`case.json` is a single object. `description` and `expect` are not sent to the
runner; the remaining fields form the request, along with the case directory.

| Key | Type | Presence | Meaning |
| --- | --- | --- | --- |
| `description` | string | Required | What the case establishes. |
| `class` | `"loader"`, `"parser"`, or `"derivation"` | Required | Which behavior the case exercises. |
| `expect` | object | Required | The expected result, using one of the shapes below. |
| `subject` | string | Required for `parser`; optional for `loader` | Project-relative source name to compile. Unless `discover_from` is supplied, its path below the case's `project/` directory is also where discovery starts. `root_canonical_name` is the canonical name the loader gives the root source unit, which is not always this value: in single-file mode the loader derives it from the base name, so a subject sixty-four directories down is reported as its base name alone. A loader case omits it when no root source is selected, such as when testing a manifest that fails to load. |
| `discover_from` | string | Optional | Path at which discovery starts, relative to the case directory rather than to `project/`. It overrides `subject` as the discovery location and is used by the nesting, boundary, and walk-up cases. |
| `workspace_roots` | array of string | Optional | Paths relative to the case directory, supplied to the loader as the host's workspace roots. An omitted value is an empty array. |
| `home_dir` | string | Optional | Path relative to the case directory, supplied to the loader as the host's home-directory boundary. This lets the suite test the home stop condition without relying on the runner's actual home directory. |
| `project_root` | string | Optional | Path relative to the case directory. When supplied, the runner uses it directly as the project root instead of searching upward. |
| `manifest_path` | string | Optional | Path relative to the case directory to an `openqasm.json` file. When supplied, the runner loads that manifest directly instead of searching for one. |

`expect` has one of four shapes:

* A loader success contains `canonical_names` and `programs`, and may also
  contain `root_canonical_name`.
* A parser success contains only `sources`.
* A derivation success contains only `derived_programs`.
* A diagnosed failure contains only `error`.

| Key | Type | Meaning |
| --- | --- | --- |
| `canonical_names` | array of string | The canonical names in the mapping, sorted by UTF-8 code units. `loader` class. |
| `root_canonical_name` | string | Optional alongside `canonical_names`. The canonical name of the subject selected as the root source unit. |
| `programs` | array of string or null | Ordered project-relative source names the project offers for compilation, or null when the manifest omitted the key. `loader` class. |
| `sources` | array of string | The canonical names incorporated into the program, in incorporation order. `parser` class. |
| `derived_programs` | array of string | Compilation roots derived from the include graph, in file-set order. `derivation` class. |
| `error` | string | An error identity from the table below. Either class. |

`expect` never contains a message string. Messages are not portable between
implementations; error identities are.

## Error identities

| Identity | Class | Raised when |
| --- | --- | --- |
| `manifest-json-invalid` | `loader` | The manifest is not well-formed JSON, or its top-level value is not an object. |
| `manifest-key-duplicate` | `loader` | An object in the manifest repeats a key. |
| `manifest-constant-nonstandard` | `loader` | The manifest contains `NaN`, `Infinity`, or `-Infinity`. |
| `manifest-integer-too-large` | `loader` | An integer anywhere in the manifest exceeds 2^53-1 in magnitude, which a JSON number held as a double cannot represent exactly. The key holding it need not be one the loader recognizes. |
| `files-name-invalid` | `loader` | A `files` or `programs` entry, or any other project-relative source name a loader validates, is empty, absolute, drive-qualified, contains a backslash, has an empty, `.` or `..` component, has a component beginning with `@`, or contains `*` or `?`. The rule and the fault are identical for every such name, so they share one identity; the diagnostic message names the key at fault. |
| `files-missing` | `loader` | A file in the file set does not exist. |
| `programs-name-unknown` | `loader` | A `programs` entry is not a member of the file set. |
| `programs-name-duplicate` | `loader` | A project-relative source name occurs more than once in `programs`. |
| `canonical-name-duplicate` | `loader` | Two entries produce the same canonical name. |
| `canonical-name-case-collision` | `loader` | Two canonical names differ only by ASCII case. |
| `canonical-name-normalization-collision` | `loader` | Two project-defined names are canonically equivalent under NFC within their collision scope. The loader preserves either spelling when it occurs alone. |
| `canonical-name-reserved` | `loader` | A project file's canonical name is the reserved standard-library name. A file selected for compilation is exempt, since nothing resolved a target to reach it. |
| `library-declaration-invalid` | `loader` | A `libraries` declaration is malformed, or names an unusable library name or a path that is not a relative POSIX path. |
| `library-missing` | `loader` | A declared library root does not exist. |
| `library-name-undeclared` | `loader` | A declared library has no manifest, or its manifest omits `name`. A library declares the name it is known by; the project referencing it cannot supply one. |
| `library-root-overlap` | `loader` | A declared library root contains, or is contained by, another root taking part in the same load. |
| `library-binding-conflict` | `loader` | Two different library roots declare the same `name`. Reaching one library under several apparent names is not this fault: it is loaded once. |
| `library-cycle` | `loader` | A library declaration closes a cycle back to a project already being loaded. |
| `containment-escape` | `loader` | A file resolves outside the root that supplies it. |
| `include-target-invalid` | `parser` | An include target is not portable: empty, absolute, drive-qualified, or containing a backslash or a `.`, `..` or empty path component. |
| `include-target-ambiguous` | `parser` | An include target matches more than one source unit, and neither candidate outranks the other. |
| `include-cycle` | `parser` | Inclusion forms a cycle. |
| `include-depth-exceeded` | `parser` | Inclusion nests deeper than the implementation supports. |
| `include-not-found` | `parser` | An include target resolves to nothing. |
| `include-version-exceeds-root` | `parser` | An included source unit declares a language version above the root's. |

A parser case loads the project before parsing it, so it may also produce any
`loader`-class identity.

Not every fault has a portable identity. A manifest that cannot be read, one
that begins with a byte-order mark, a `files` or `programs` value that is not an
array of strings, and a source file that exists but cannot be read are all
errors, but they carry no agreed identity and no case asserts one. An
implementation reports them however it wishes.

A runner has to turn its implementation's exception into one of these
identities. The reference runner accepts the exception's machine-readable
identity only when it belongs to the corpus vocabulary above. Diagnostic
message text is never consulted: it is not portable between implementations,
and matching it would report the wrong identity after a harmless reword. An
exception with no portable identity is left unnamed rather than given a
catch-all, so a fault the corpus never named is reported as a runner failure
rather than as a passing case.

## Process contract

A runner is a program that reads one JSON object from standard input and writes
one JSON object to standard output.

Input:

```json
{
  "case_dir": "/absolute/path/to/conformance/project/cases/33-programs-accepted",
  "class": "loader",
  "subject": "a.qasm",
  "discover_from": null,
  "workspace_roots": [],
  "home_dir": null,
  "project_root": null,
  "manifest_path": null
}
```

`case_dir` and `class` are always present. For the optional scalar fields
`subject`, `discover_from`, `home_dir`, `project_root`, and `manifest_path`, a
runner must treat an absent key and JSON `null` the same way. An absent or `null`
`workspace_roots` is equivalent to an empty array.

Output on loader success:

```json
{
  "canonical_names": ["a.qasm", "b.qasm", "lib/helper.inc"],
  "root_canonical_name": "a.qasm",
  "programs": ["b.qasm", "a.qasm"]
}
```

Output on derivation success:

```json
{ "derived_programs": ["z-main.qasm", "a-independent.qasm"] }
```

Output on a diagnosed failure:

```json
{ "error": "canonical-name-reserved" }
```

Exit code `0` means the runner produced a result, whether that result is a
success or a diagnosed error. A non-zero exit code means the runner itself
failed, which is a suite failure rather than a case result.

A runner that cannot parse skips both parser-dependent classes by writing
`{ "skipped": "parser class not implemented" }` and exits `0`.

Each output object is exactly one closed variant. A diagnosed failure contains
only `error`; a parser success contains only `sources`; a loader success
contains `canonical_names` and `programs`, with `root_canonical_name` only when
a subject makes it applicable; a derivation success contains only
`derived_programs`; and a skip contains only `skipped`. Combining variants,
omitting a required key, or adding an unknown key is an invalid case result.

`canonical_names` is always sorted by UTF-8 code units before comparison, so
that a runner's internal ordering is not under test. `sources` is not sorted,
because incorporation order is part of what the case establishes. `programs`
preserves manifest order and is always unique. For `programs`, JSON `null`
means the key was absent; an empty array is an explicit declaration and remains
distinct from absence. `derived_programs` is not sorted because its file-set
order is the fallback contract being tested.

### Where discovery starts, and what happens when it finds nothing

Discovery starts at the case-relative path in `discover_from` when supplied.
Otherwise it starts at the path formed by resolving `subject` below the case's
`project/` directory, or at `project/` itself when there is no subject. A
supplied `project_root` or `manifest_path` bypasses the upward search and loads
that project directly. When `subject` is also supplied, it remains the selected
compilation root and receives the same reserved-name exemption as a subject
selected through discovery.

When discovery finds no manifest, the case is in **single-file mode**. If the
initial search location is a file, that file is the whole compilation and its
base name is its canonical name. If the initial search location is not a file,
the project is empty and has no source units. Either way there is no manifest,
so a runner that reports `programs` reports it as `null`.

A case may omit `subject`, which is how a case about a manifest that fails to
load says it has nothing to compile. Such a case reports `canonical_names`
without a `root_canonical_name`. The `parser` class needs something to compile,
so a `parser` case without a `subject` is invalid under the process contract. A
`derivation` case omits `subject` because it loads the whole project without
selecting a compilation root.

## Deliberately untested

These are implementation-defined, and a case must not assert a particular
answer:

* **The concrete inclusion-depth ceiling.** The project definition states a floor
  of 15 and an implementation may support far more. Case `08` derives its chain
  length from the ceiling the implementation reports rather than fixing a number.
  The walk-up bound is deliberately *not* in this list; see "Two bounds,
  tested differently" below.
* **Diagnostic message text.** Only error identities are compared.
* **Whether a host consults unsaved editor buffers**, and what canonical name it
  gives to a source unit that has no location, such as a notebook cell.
* **Physical file identity.** Two canonical names that reach the same bytes are
  two source units, and no case asserts otherwise.
* **The order in which independent errors are reported** when a project contains
  more than one fault.

## Include resolution

The language specification fixes how an include target becomes candidate
canonical names: a bare target names a source unit beside the includer and one
from the root of the includer's library, and neither outranks the other. This
project definition supplies the source mapping those names are looked up in. It
adds no precedence of its own, so a target matching more than one source unit is
an error rather than a win for either.

| Case | Behavior established |
| --- | --- |
| `29-include-reaches-out-of-directory` | Only one candidate exists, so the target resolves. |
| `30-ambiguous-include-target` | Both candidates exist, which is diagnosed as `include-target-ambiguous`. |
| `49-root-relative-disambiguation` | Writing the target from the root of the includer's library names one source unit, which resolves. |

These cases test compatibility with the non-normative project profile. They do
not establish OpenQASM language conformance.

### Libraries

Cases `50` through `61`, `67`, and `74` cover libraries. A library is a project loaded
from a root outside the one referencing it, and each of these cases keeps the
library beside the case's `project/` directory so that the declared path escapes
the project root as the rules require.

Two names are in play. A `libraries` key is the *apparent name*: what the
project writing it calls that library, chosen locally. The library's own `name`
is its *canonical name*, and it is what `@name/` carries in every canonical name
the library's files take. `@` belongs to neither name; it introduces the library
selector. A library must declare a `name`, because a name chosen by whichever
project happens to reference it would make the same library a different library
in each.

A runner establishes this only if it scopes apparent names per project. The
source inventory and owner-local bindings form one environment; dropping the
bindings restores an unscoped fallback in which every library is reachable from
everywhere, which cases `58` and `59` detect.

| Case | Behavior established |
| --- | --- |
| `50-library-loaded` | A declared library's files are loaded under the name it declares. |
| `51-library-of-a-library` | A library may declare libraries of its own, loaded as projects in turn. |
| `52-library-root-overlap` | A library root inside the referencing project is diagnosed. |
| `53-library-binding-conflict` | Two roots declaring one `name` are diagnosed. |
| `54-library-cycle` | A declaration closing a cycle is diagnosed. |
| `55-library-prefix-reserved` | A project-relative name may not have a component beginning with `@`. |
| `56-deep-library-cycle` | A transitive declaration returning to an active library root is diagnosed. |
| `57-library-two-apparent-names` | One library reached under two apparent names is loaded once. |
| `58-library-apparent-names-are-local` | Two projects each writing one word for a different library both resolve. |
| `59-library-undeclared-transitive` | A library only a dependency declares is not reachable from this project. |
| `60-library-manifest-absent` | A declared library with no manifest is diagnosed. |
| `61-library-name-undeclared` | A declared library whose manifest omits `name` is diagnosed. |
| `67-library-roots-overlap` | Two library roots where one contains the other are diagnosed. |
| `74-portable-name-characters` | Square and curly brackets remain exact characters in project source names, apparent library names, canonical library names, and library source names. |

## Case groups

### Declared programs

Cases `31` through `36` cover declared programs. They distinguish accepted,
absent, and explicitly empty declarations, and reject unknown, invalid, and
duplicate roots. These are host-integration concerns, not language features.

### Derived programs

Case `77-programs-derived` covers the parser-dependent fallback used only when
the manifest omits `programs`. Its included helper is not a compilation root,
and its two remaining roots preserve file-set order rather than lexical order.
This result is distinct from loader output: `programs: null` reports that the
manifest declared nothing, while `derived_programs` reports the fallback roots
computed from source text.

### Discovery and file-set edges

Cases `43` through `47`, `62`, `63`, `66`, `68`, `75`, and `76` close the
boundary and defaulting edges of the project contract:

| Case | Behavior established |
| --- | --- |
| `43-home-boundary-stop` | The upward search does not inspect the user's home directory or anything above it. |
| `44-explicit-project-root` | A project root supplied by the caller is loaded directly without upward discovery. |
| `45-explicit-manifest-path` | A manifest path supplied by the caller is loaded directly without upward discovery. |
| `46-empty-files-list` | An explicit `"files": []` is an empty file set, not a request for the default walk. |
| `47-hidden-entry-excluded` | The default walk skips source files and directories whose names begin with `.`. |
| `62-walk-stops-at-nested-manifest` | The default walk does not descend into a directory holding its own manifest. |
| `63-walk-stops-at-repository-marker` | The default walk does not descend into a directory that is a repository of its own. |
| `68-walk-stops-at-git-marker` | The same, for `.git` itself. Generated, since a nested `.git` cannot be committed. |
| `66-reserved-name-compilation-root` | A file selected for compilation may take the reserved standard-library name. |
| `75-explicit-project-root-reserved-compilation-root` | A subject remains the selected compilation root when the caller supplies the project root directly. |
| `76-explicit-manifest-path-reserved-compilation-root` | A subject remains the selected compilation root when the caller supplies the manifest path directly. |

The two explicit-entry cases select `stdgates.inc`, proving the exemption is
preserved when discovery is bypassed. Without a selected subject, the same file
remains reserved; the literal runner tests exercise that negative side in both
explicit modes.

The markers a walk stops at are `.git`, `.hg`, `.svn` and `.jj`, tested for existence rather than for being directories, since a worktree records `.git` as a file. Two cases cover the rule because neither alone is enough: `68` uses `.git` and must be generated, since git refuses to track a nested `.git` entry, while `63` is committed and uses `.hg`, which is what establishes that the marker set is more than git alone.

### Manifest validation

A loader ignores a manifest key it does not recognize, but its value still obeys format-wide JSON restrictions. The remaining cases cover those restrictions and library declarations:

| Case | Behavior established |
| --- | --- |
| `69-manifest-integer-too-large` | An integer too large to survive a double is diagnosed, even under an unrecognized key. |
| `70-library-missing` | A declared library whose root directory does not exist is diagnosed. |
| `71-libraries-not-an-object` | The `libraries` key must be an object. |
| `72-library-declared-as-a-string` | A library is declared as an object, not a bare path string. |
| `73-library-path-absolute` | A library `path` is relative to the declaring manifest. |

### Generated cases

Nine cases cannot be committed as ordinary files and are materialized at run
time by `generated/generate.py`:

| Case | Why it cannot be committed |
| --- | --- |
| `03-repo-boundary-stop` | Needs a directory named `.git`, which git will not track. A committed copy would silently ship without the marker the case exists to test. |
| `08-depth-exceeded` | Its depth depends on the implementation's ceiling, which is implementation-defined above the floor of 15 the project definition states. |
| `10-symlink-escape` | Needs a symbolic link pointing outside the tree. |
| `11-symlink-internal` | Needs a symbolic link, and not every checkout preserves one. |
| `20-unicode-normalization` | Needs a file whose name is stored decomposed. Version-control tooling on some platforms normalizes names on add, so committing this case would silently destroy the thing it tests. |
| `27-walk-up-bound-reached` | A 63-directory-deep tree, impractical to store and would dominate the repository's file count. |
| `28-walk-up-bound-exceeded` | A 64-directory-deep tree, for the same reason. |
| `42-containment-escape` | Needs a symbolic link pointing outside the project root, so that a declared file resolves outside it. |
| `68-walk-stops-at-git-marker` | Needs a nested directory named `.git`, for the same reason as `03`. |

When the host cannot support a case, the generator reports and skips it. The
symbolic-link cases are skipped where the host cannot create a symbolic link;
the Unicode case is skipped on a file system that normalizes names on creation.

### Two bounds, tested differently

The suite contains two numeric limits and treats them differently on purpose.

The **inclusion depth** is a floor. The language leaves any depth limit
implementation defined, and the project definition states a minimum of 15 that an
implementation may exceed, so `08-depth-exceeded` derives its chain from the
ceiling the implementation reports and the concrete ceiling is listed as untested
above. `07-depth-15` asserts the floor itself.

The **walk-up bound** is a fixed contract value. The project definition states
it as exactly 64 directories examined, not as a floor. An implementation that
examines a different number may find a project where a conforming one finds
none, and compile a different program as a result.
`27-walk-up-bound-reached` and `28-walk-up-bound-exceeded` therefore test 64 as
written, without parameterizing it. If that value ever becomes implementation-
defined, these two cases change with it.

The pair exists because an off-by-one here is invisible in every realistic
directory layout and silently disagreeing about it is exactly the failure the
suite is for. Case 28 is the discriminating one: an implementation that examines
65 directories finds a project where a conforming one finds none.

## Running

From the repository root, with the development dependencies and parser extra
installed in the active Python environment:

```console
PYTHONPATH=source/openqasm python conformance/project/harness.py --runner 'python conformance/project/runners/python/runner.py'
```

The harness enumerates the committed cases, materializes the generated ones into
a temporary directory, runs each case through the runner, and reports every
outcome. It exits non-zero if any case fails or the runner fails as a program,
and zero when the only non-passes are skips. `--json` writes a machine-readable
summary instead, and `--depth-ceiling` supplies the inclusion depth the
implementation under test supports, which is implementation-defined above the
specified minimum of 15.

A runner is supplied per implementation. The Python one under `runners/python/`
is the worked example of the process contract; a runner in another language is
what this corpus exists for.

## What a passing run establishes

A green run of one runner establishes that the process contract above is
implementable, that this corpus is internally consistent, and that the runner's
implementation agrees with the expectations recorded here.

It does not establish cross-implementation conformance. One runner agreeing with
the corpus is one implementation agreeing with itself and with the expectations
that were written alongside it. The claim this corpus exists to support becomes
available only when a second runner, written independently and in another
language, passes the same cases. Until then, a green run means the suite is
ready for that second implementation, not that agreement has been demonstrated.
