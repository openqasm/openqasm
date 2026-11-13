#!/usr/bin/env python3
"""Run the OpenQASM project conformance corpus against any conforming runner.

The runner is reached only through the process contract in ``README.md``: the
harness spawns it, writes one JSON object to its standard input, and reads one
JSON object from its standard output.  Nothing here knows what language the
runner is written in, and nothing here imports the implementation under test.

    python harness.py --runner 'python3 runners/python/runner.py'

A valid case result has one of three outcomes.  It passes when the runner's
result matches the case's expectation.  It fails when the result disagrees.  It
is skipped when the runner declines it, because the runner does not implement
the case class, or when this host cannot materialize a generated case at all.
A skip is never counted as a pass.

A runner that exits non-zero or does not write exactly one JSON object has
failed as a program, which the contract calls a suite failure rather than a case
result.  Those are reported separately, so a broken runner is never mistaken
for a case that legitimately disagrees.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")
GENERATOR = os.path.join(HERE, "generated", "generate.py")
MANIFEST_NAME = "openqasm.json"

# The inclusion depth ceiling is implementation-defined above the specified
# minimum of 15.  The harness cannot import a constant from a runner written in
# another language, so the ceiling is supplied here and documented rather than
# guessed.  This default matches the reference implementation.
DEFAULT_DEPTH_CEILING = 64

PASS = "pass"
FAIL = "fail"
SKIP = "skip"
RUNNER_FAILURE = "runner-failure"

_RESULT_DISCRIMINATORS = frozenset(
    ("error", "sources", "canonical_names", "derived_programs", "skipped")
)
_RESULT_KEYS = {
    "error": (frozenset(("error",)), frozenset(("error",))),
    "sources": (frozenset(("sources",)), frozenset(("sources",))),
    "canonical_names": (
        frozenset(("canonical_names", "programs")),
        frozenset(("canonical_names", "root_canonical_name", "programs")),
    ),
    "derived_programs": (
        frozenset(("derived_programs",)),
        frozenset(("derived_programs",)),
    ),
    "skipped": (frozenset(("skipped",)), frozenset(("skipped",))),
}
_EXPECTATION_KEYS = {
    discriminator: keys
    for discriminator, keys in _RESULT_KEYS.items()
    if discriminator != "skipped"
}


class HarnessError(Exception):
    """The corpus cannot be run at all, so no case outcome is meaningful."""


def _sorted_by_code_units(names: Sequence[str]) -> List[str]:
    return sorted(names, key=lambda name: name.encode("utf-8"))


def _read_case(directory: str) -> Dict[str, Any]:
    with open(os.path.join(directory, "case.json"), "r", encoding="utf-8") as stream:
        return json.load(stream)


def _case_dirs(parent: str) -> List[Tuple[str, str]]:
    # A case directory is one that holds a case.json.  The generator also creates
    # a sibling directory to hold the target of the escaping symbolic link, and
    # that is not a case.
    names = sorted(
        name
        for name in os.listdir(parent)
        if os.path.isfile(os.path.join(parent, name, "case.json"))
    )
    return [(name, os.path.join(parent, name)) for name in names]


def _committed_case_dirs() -> List[Tuple[str, str]]:
    if not os.path.isdir(CASES):
        raise HarnessError("no committed cases at %s" % CASES)
    return _case_dirs(CASES)


def _assert_free_of_manifests(directory: str) -> None:
    """Fail loudly if any ancestor of ``directory`` holds a manifest.

    Several generated cases assert that discovery finds *no* project.  Discovery
    searches upwards, and the process contract has no field with which a runner
    could be told where to stop, so a manifest anywhere above the materialization
    directory would silently turn a negative case into a positive one.
    """
    current = os.path.abspath(directory)
    while True:
        if os.path.isfile(os.path.join(current, MANIFEST_NAME)):
            raise HarnessError(
                "%s holds a manifest and is an ancestor of the materialization directory,"
                " so the generated negative-discovery cases would not mean what they say" % current
            )
        parent = os.path.dirname(current)
        if parent == current:
            return
        current = parent


def _materialize(out: str, depth_ceiling: int) -> List[Tuple[str, str]]:
    _assert_free_of_manifests(os.path.dirname(os.path.abspath(out)))
    result = subprocess.run(
        [sys.executable, GENERATOR, "--out", out, "--depth-ceiling", str(depth_ceiling)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise HarnessError("the generator failed: %s" % result.stderr.strip())
    return _case_dirs(out)


def expected_generated_names() -> List[str]:
    """The generated cases the generator would produce on a host that supports all of them."""
    return [
        "03-repo-boundary-stop",
        "08-depth-exceeded",
        "10-symlink-escape",
        "11-symlink-internal",
        "20-unicode-normalization",
        "27-walk-up-bound-reached",
        "28-walk-up-bound-exceeded",
        "42-containment-escape",
        "68-walk-stops-at-git-marker",
    ]


def _request(case: Dict[str, Any], case_dir: str) -> Dict[str, Any]:
    return {
        "case_dir": os.path.abspath(case_dir),
        "class": case["class"],
        "subject": case.get("subject"),
        "discover_from": case.get("discover_from"),
        "workspace_roots": case.get("workspace_roots", []),
        "home_dir": case.get("home_dir"),
        "project_root": case.get("project_root"),
        "manifest_path": case.get("manifest_path"),
    }


def _invoke(command: Sequence[str], request: Dict[str, Any]) -> Dict[str, Any]:
    """Run the runner once and return its result object.

    :raises HarnessError: The runner exited non-zero or did not write exactly one
        JSON object, either of which is a suite failure rather than a case result.
    """
    completed = subprocess.run(
        list(command),
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise HarnessError(
            "runner exited %d: %s" % (completed.returncode, completed.stderr.strip())
        )
    try:
        result = json.loads(completed.stdout)
    except ValueError as exc:
        raise HarnessError(
            "runner did not write a JSON object: %s (stdout was %r)" % (exc, completed.stdout)
        ) from exc
    if not isinstance(result, dict):
        raise HarnessError("runner wrote %s, not a JSON object" % type(result).__name__)
    return result


def _runner_command(
    command: str,
    platform: Optional[str] = None,
    command_processor: Optional[str] = None,
) -> List[str]:
    if not command.strip():
        return []
    platform = os.name if platform is None else platform
    if platform == "nt":
        processor = command_processor or os.environ.get("COMSPEC", "cmd.exe")
        return [processor, "/d", "/s", "/c", command]
    return shlex.split(command)


def _value_shape_disagreement(
    value: Dict[str, Any], discriminator: str, variant: str
) -> Optional[str]:
    """Return why one closed variant has values of the wrong JSON types."""
    if discriminator in ("error", "skipped"):
        if not isinstance(value[discriminator], str):
            return "%s field %r must be a string, got %r" % (
                variant,
                discriminator,
                value[discriminator],
            )
        return None

    if discriminator in ("sources", "derived_programs"):
        names = value[discriminator]
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            return "%s field %r must be an array of strings, got %r" % (
                variant,
                discriminator,
                names,
            )
        return None

    names = value["canonical_names"]
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        return "%s field 'canonical_names' must be an array of strings, got %r" % (
            variant,
            names,
        )
    programs = value["programs"]
    if programs is not None and (
        not isinstance(programs, list) or not all(isinstance(name, str) for name in programs)
    ):
        return "%s field 'programs' must be null or an array of strings, got %r" % (
            variant,
            programs,
        )
    root_name = value.get("root_canonical_name")
    if "root_canonical_name" in value and not isinstance(root_name, str):
        return "%s field 'root_canonical_name' must be a string, got %r" % (
            variant,
            root_name,
        )
    return None


def _result_shape_disagreement(result: Dict[str, Any]) -> Optional[str]:
    """Return why ``result`` is not one exact process-contract variant."""
    keys = frozenset(result)
    discriminators = keys & _RESULT_DISCRIMINATORS
    if len(discriminators) != 1:
        return "result must contain exactly one discriminator, got %r" % result

    discriminator = next(iter(discriminators))
    required, allowed = _RESULT_KEYS[discriminator]
    missing = required - keys
    if missing:
        return "result variant %r is missing keys %r" % (discriminator, sorted(missing))
    unknown = keys - allowed
    if unknown:
        return "result variant %r has unknown keys %r" % (discriminator, sorted(unknown))
    return _value_shape_disagreement(result, discriminator, "result")


def _expectation_shape_disagreement(expect: Dict[str, Any]) -> Optional[str]:
    """Return why ``expect`` is not one exact comparable-result variant."""
    keys = frozenset(expect)
    discriminators = keys & frozenset(_EXPECTATION_KEYS)
    if len(discriminators) != 1:
        return "expectation must contain exactly one discriminator, got %r" % expect

    discriminator = next(iter(discriminators))
    required, allowed = _EXPECTATION_KEYS[discriminator]
    missing = required - keys
    if missing:
        return "expectation variant %r is missing keys %r" % (discriminator, sorted(missing))
    unknown = keys - allowed
    if unknown:
        return "expectation variant %r has unknown keys %r" % (discriminator, sorted(unknown))
    return _value_shape_disagreement(expect, discriminator, "expectation")


def _compare(expect: Dict[str, Any], result: Dict[str, Any]) -> Optional[str]:
    """Return a description of the disagreement, or ``None`` when they agree.

    Comparison follows the contract rather than any implementation.  Canonical
    names are sorted by UTF-8 code units on both sides, because a runner's
    internal ordering is not under test.  Sources and derived programs are
    compared in order, because incorporation and file-set order are part of
    what their respective case classes establish.  An error is compared as an
    identity, never as message text.
    """
    shape_disagreement = _result_shape_disagreement(result)
    if shape_disagreement is not None:
        return shape_disagreement

    if "error" in expect:
        if "error" not in result:
            return "expected error %r, got %r" % (expect["error"], result)
        if result["error"] != expect["error"]:
            return "expected error %r, got error %r" % (expect["error"], result["error"])
        return None

    if "sources" in expect:
        if "sources" not in result:
            return "expected sources %r, got %r" % (expect["sources"], result)
        if list(result["sources"]) != list(expect["sources"]):
            return "expected sources %r, got %r" % (expect["sources"], result["sources"])
        return None

    if "derived_programs" in expect:
        if "derived_programs" not in result:
            return "expected derived programs %r, got %r" % (
                expect["derived_programs"],
                result,
            )
        if list(result["derived_programs"]) != list(expect["derived_programs"]):
            return "expected derived programs %r, got %r" % (
                expect["derived_programs"],
                result["derived_programs"],
            )
        return None

    if "canonical_names" in expect:
        if "canonical_names" not in result:
            return "expected canonical names %r, got %r" % (expect["canonical_names"], result)
        wanted = _sorted_by_code_units(expect["canonical_names"])
        got = _sorted_by_code_units(result["canonical_names"])
        if got != wanted:
            return "expected canonical names %r, got %r" % (wanted, got)
        if (
            "root_canonical_name" in expect
            and result.get("root_canonical_name") != expect["root_canonical_name"]
        ):
            return "expected root canonical name %r, got %r" % (
                expect["root_canonical_name"],
                result.get("root_canonical_name"),
            )
        if "root_canonical_name" not in expect and "root_canonical_name" in result:
            return "expected no root canonical name, got %r" % result["root_canonical_name"]
        if "programs" in expect and result.get("programs") != expect["programs"]:
            return "expected programs %r, got %r" % (expect["programs"], result.get("programs"))
        return None

    return "case declares no comparable expectation: %r" % expect


def run_case(command: Sequence[str], name: str, case_dir: str) -> Dict[str, Any]:
    """Run one case and classify its outcome."""
    case = _read_case(case_dir)
    expectation_disagreement = _expectation_shape_disagreement(case["expect"])
    if expectation_disagreement is not None:
        return {"case": name, "outcome": FAIL, "reason": expectation_disagreement}
    try:
        result = _invoke(command, _request(case, case_dir))
    except HarnessError as exc:
        return {"case": name, "outcome": RUNNER_FAILURE, "reason": str(exc)}

    shape_disagreement = _result_shape_disagreement(result)
    if shape_disagreement is not None:
        return {"case": name, "outcome": FAIL, "reason": shape_disagreement}
    if "skipped" in result:
        return {"case": name, "outcome": SKIP, "reason": result["skipped"]}

    disagreement = _compare(case["expect"], result)
    if disagreement is None:
        return {"case": name, "outcome": PASS}
    return {"case": name, "outcome": FAIL, "reason": disagreement}


def run_corpus(command: Sequence[str], out: str, depth_ceiling: int) -> Dict[str, Any]:
    """Run the whole corpus, committed and generated, against ``command``."""
    results = []
    for name, case_dir in _committed_case_dirs():
        results.append(run_case(command, name, case_dir))

    generated = _materialize(out, depth_ceiling)
    produced = {name for name, _ in generated}
    for name, case_dir in generated:
        results.append(run_case(command, name, case_dir))
    for name in expected_generated_names():
        if name not in produced:
            results.append(
                {
                    "case": name,
                    "outcome": SKIP,
                    "reason": "this host cannot materialize the case",
                }
            )

    counts = {PASS: 0, FAIL: 0, SKIP: 0, RUNNER_FAILURE: 0}
    for entry in results:
        counts[entry["outcome"]] += 1
    return {"cases": sorted(results, key=lambda entry: entry["case"]), "counts": counts}


def _report(summary: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        json.dump(summary, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return
    for entry in summary["cases"]:
        line = "%-6s %s" % (entry["outcome"], entry["case"])
        if entry.get("reason"):
            line += "  (%s)" % entry["reason"]
        print(line)
    counts = summary["counts"]
    print(
        "\n%d passed, %d failed, %d skipped, %d runner failures"
        % (counts[PASS], counts[FAIL], counts[SKIP], counts[RUNNER_FAILURE])
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runner",
        required=True,
        help="command that runs one case, for example 'python3 runners/python/runner.py'",
    )
    parser.add_argument(
        "--depth-ceiling",
        type=int,
        default=DEFAULT_DEPTH_CEILING,
        help="the inclusion depth the implementation under test supports (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="directory to materialize generated cases into (default: a temporary directory)",
    )
    parser.add_argument("--json", action="store_true", help="write a machine-readable summary")
    arguments = parser.parse_args(argv)

    command = _runner_command(arguments.runner)
    if not command:
        print("--runner must name a command", file=sys.stderr)
        return 2

    temporary = arguments.out is None
    out = arguments.out or os.path.join(tempfile.mkdtemp(prefix="oq-conformance-"), "generated")
    try:
        summary = run_corpus(command, out, arguments.depth_ceiling)
    except HarnessError as exc:
        print("harness failure: %s" % exc, file=sys.stderr)
        return 2
    finally:
        if temporary:
            shutil.rmtree(os.path.dirname(out), ignore_errors=True)

    _report(summary, arguments.json)
    counts = summary["counts"]
    if counts[FAIL] or counts[RUNNER_FAILURE]:
        return 1
    if not counts[PASS]:
        # A runner that skips everything would otherwise report success having run nothing.
        print(
            "harness failure: no case passed; %d were skipped" % counts[SKIP],
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
