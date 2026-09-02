#!/usr/bin/env python3
"""Reference runner for the OpenQASM project conformance corpus.

Reads one JSON object describing a case from standard input and writes one JSON
object describing the result to standard output.  Exit code ``0`` means a result
was produced, whether that result is a success, a diagnosed error, or a skip.  A
non-zero exit code means this runner itself failed, so the case outcome is
unknown and the suite treats it as a suite failure rather than a case result.

Standard output carries the result object and nothing else, so every diagnostic
goes to standard error.

The process contract is defined in ``conformance/project/README.md``.  This
runner is its reference worked example, making these key behaviors explicit for
implementers of runners in other languages:

* Discovery starts at ``discover_from`` when present, otherwise at ``subject``
    inside the case's ``project`` directory, or at that directory itself when
    there is no subject.
* ``discover_from``, ``workspace_roots``, ``home_dir``, ``project_root``, and
    ``manifest_path`` are relative to the case directory.  ``subject`` is a
    project-relative source name within the loaded project.  The runner validates
    it and reports it unchanged as ``root_canonical_name``.
* A case may bypass the upward walk by supplying ``project_root`` or
    ``manifest_path``.  Those are caller-designated entry points and are used
    directly.  A supplied ``subject`` remains the selected compilation root.
* When discovery finds no project, the case is in single-file mode.  If the
    discovery start is a file, that file is the whole compilation and its base
    name is its canonical name.  Otherwise, the project has no source units.
    Either way there is no manifest, so ``programs`` is reported as ``null``.
* A case may omit ``subject``, which is how a case about a manifest that fails
    to load says it has nothing to compile.  Such a case reports canonical names
    without a ``root_canonical_name``.  A ``parser`` case without a ``subject`` is
    malformed because it names nothing to compile.  A ``derivation`` case omits
    it deliberately because the runner derives every compilation root.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence


class RunnerFailure(Exception):
    """The runner cannot produce a result, so the case outcome is unknown."""


_CORPUS_ERROR_IDENTITIES = frozenset(
    (
        "manifest-json-invalid",
        "manifest-key-duplicate",
        "manifest-constant-nonstandard",
        "manifest-integer-too-large",
        "files-name-invalid",
        "files-missing",
        "programs-name-unknown",
        "programs-name-duplicate",
        "canonical-name-duplicate",
        "canonical-name-case-collision",
        "canonical-name-normalization-collision",
        "canonical-name-reserved",
        "library-declaration-invalid",
        "library-missing",
        "library-name-undeclared",
        "library-root-overlap",
        "library-binding-conflict",
        "library-cycle",
        "containment-escape",
        "include-target-invalid",
        "include-target-ambiguous",
        "include-cycle",
        "include-depth-exceeded",
        "include-not-found",
        "include-version-exceeds-root",
    )
)


def _parser_available() -> bool:
    try:
        import antlr4  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        return False
    return True


def _identity_of(error: BaseException) -> Optional[str]:
    """Return the corpus error identity for ``error``, or ``None`` if unmapped.

    The implementation supplies a machine-readable identity, which is accepted only
    when the corpus defines it.  This preserves subclass identities without exposing
    implementation-private errors.  Diagnostic message text is never consulted:
    messages are not portable between implementations, and matching them would
    report the wrong identity after a harmless reword.

    An exception whose ``identity`` is ``None`` is not given one here.  The base
    :class:`~openqasm3.resolver.IncludeError` is raised for a condition the
    corpus deliberately does not name, and inventing a catch-all would report a
    passing case where the corpus expects the runner to fail.
    """
    identity = getattr(error, "identity", None)
    if isinstance(identity, str) and identity in _CORPUS_ERROR_IDENTITIES:
        return identity
    return None


def _string_field(request: Dict[str, Any], key: str, required: bool) -> Optional[str]:
    if key not in request or request[key] is None:
        if required:
            raise RunnerFailure("input object is missing required key %r" % key)
        return None
    value = request[key]
    if not isinstance(value, str):
        raise RunnerFailure("input key %r must be a string, got %r" % (key, value))
    return value


def _path_list(request: Dict[str, Any], key: str) -> List[str]:
    value = request.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        raise RunnerFailure("input key %r must be an array of strings, got %r" % (key, value))
    return value


def _under(base: str, relative: str) -> str:
    return os.path.join(base, *relative.split("/"))


def _parse(loaded: Any, root_name: str) -> Dict[str, Any]:
    import openqasm3  # pylint: disable=import-outside-toplevel

    program = openqasm3.parse_project(loaded, root_name)
    # Incorporation order is part of what a parser-class case establishes, so
    # this list is deliberately not sorted.
    return {"sources": [unit.canonical_name for unit in program.sources]}


def _derive(loaded: Any) -> Dict[str, Any]:
    import openqasm3  # pylint: disable=import-outside-toplevel

    programs = openqasm3.derive_programs(loaded)
    return {"derived_programs": list(programs)}


def _execute(
    case_dir: str,
    case_class: str,
    subject: Optional[str],
    discover_from: Optional[str],
    workspace_roots: Sequence[str],
    home_dir: Optional[str],
    project_root: Optional[str],
    manifest_path: Optional[str],
) -> Dict[str, Any]:
    from openqasm3.project import (  # pylint: disable=import-outside-toplevel
        canonical_name,
        discover,
        load_project,
        load_target,
        read_manifest,
    )

    tree = os.path.join(case_dir, "project")
    subject_name = canonical_name(subject) if subject is not None else None
    if case_class == "parser" and subject_name is None:
        raise RunnerFailure("a 'parser' case must name a subject to compile")
    if case_class == "derivation" and subject_name is not None:
        raise RunnerFailure("a 'derivation' case must not name a subject")
    if discover_from:
        start = _under(case_dir, discover_from)
    elif subject_name:
        start = _under(tree, subject_name)
    else:
        start = tree
    roots = [_under(case_dir, entry) for entry in workspace_roots]
    root_name: Optional[str] = subject_name
    report_root_name = subject_name is not None

    if project_root is not None:
        root = _under(case_dir, project_root)
        loaded = load_project(root, compilation_root=subject_name)
    elif manifest_path is not None:
        manifest = _under(case_dir, manifest_path)
        root = os.path.dirname(manifest)
        loaded = load_project(
            root,
            manifest=read_manifest(manifest),
            compilation_root=subject_name,
        )
    else:
        home = _under(case_dir, home_dir) if home_dir is not None else None
        if discover_from is None and subject_name is not None:
            loaded = load_target(start, workspace_roots=roots, home_dir=home)
            root_name = loaded.compilation_root
        else:
            discovered_root = discover(start, workspace_roots=roots, home_dir=home)
            if discovered_root is not None:
                loaded = load_project(discovered_root, compilation_root=subject_name)
            elif os.path.isfile(start):
                loaded = load_target(start, workspace_roots=roots, home_dir=home)
                root_name = loaded.compilation_root
            elif case_class == "derivation":
                return {"derived_programs": []}
            else:
                return {"canonical_names": [], "programs": None}

    sources: Dict[str, str] = loaded.sources
    if report_root_name and root_name not in sources:
        raise RunnerFailure("subject %r is not a source unit of the project" % root_name)
    if case_class == "derivation":
        return _derive(loaded)
    if case_class == "loader":
        # Sorted by UTF-8 code units, so that no runner's internal ordering is
        # under test.
        names = sorted(sources, key=lambda name: name.encode("utf-8"))
        result: Dict[str, Any] = {
            "canonical_names": names,
            "programs": None if loaded.programs is None else list(loaded.programs),
        }
        if report_root_name:
            result["root_canonical_name"] = root_name
        return result

    if root_name is None:
        raise RunnerFailure("a parser case must resolve a compilation root")
    return _parse(loaded, root_name)


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    """Run one case and return its result object."""
    if not isinstance(request, dict):
        raise RunnerFailure("input must be a JSON object, got %r" % type(request).__name__)

    case_dir = _string_field(request, "case_dir", required=True)
    case_class = _string_field(request, "class", required=True)
    if case_class not in ("loader", "parser", "derivation"):
        raise RunnerFailure("unknown case class %r" % case_class)

    if case_class in ("parser", "derivation") and not _parser_available():
        return {"skipped": "parser class not implemented"}

    subject = _string_field(request, "subject", required=False)
    discover_from = _string_field(request, "discover_from", required=False)
    workspace_roots = _path_list(request, "workspace_roots")
    home_dir = _string_field(request, "home_dir", required=False)
    project_root = _string_field(request, "project_root", required=False)
    manifest_path = _string_field(request, "manifest_path", required=False)

    assert case_dir is not None  # guaranteed by required=True above
    try:
        return _execute(
            case_dir,
            case_class,
            subject,
            discover_from,
            workspace_roots,
            home_dir,
            project_root,
            manifest_path,
        )
    except RunnerFailure:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        identity = _identity_of(exc)
        if identity is None:
            # An exception this runner cannot name is a runner failure, never an
            # identity.  Reporting it as one would invent agreement.
            raise
        return {"error": identity}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Read one case from standard input and write one result to standard output."""
    if argv:
        print("usage: runner.py < case-input.json", file=sys.stderr)
        return 2
    try:
        request = json.load(sys.stdin)
    except ValueError as exc:
        print("input is not valid JSON: %s" % exc, file=sys.stderr)
        return 2

    try:
        result = run(request)
    except RunnerFailure as exc:
        print("runner failure: %s" % exc, file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print("runner failure: unmapped %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
