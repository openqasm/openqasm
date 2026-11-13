#!/usr/bin/env python3
"""Materialize conformance cases that cannot reliably live in a checkout.

Nine cases need something a checkout cannot represent portably or practically:
a nested ``.git`` directory, a symbolic link, a decomposed filename that some
file systems or tooling normalize, a chain whose depth depends on the
implementation under test, or a tree deep enough to dominate the repository's
file count.

The harness runs this automatically.  Run it directly only to inspect the
materialized cases::

    python generate.py --out /tmp/oq-generated

This script uses only the Python standard library and does not import the
package under test.
"""

import argparse
import json
import os
import shutil
import sys
import unicodedata

MARKER_NAME = ".generated-by-generate-py"
"""Marks a directory this generator owns and may therefore erase."""

# The specification requires support for an inclusion depth of at least 15, and
# an implementation may support far more.  A runner passes its own ceiling so
# that the depth case tests "one deeper than you support" rather than a number
# this file guessed.
DEFAULT_DEPTH_CEILING = 64

# The walk-up bound is different: the project definition states it as exactly
# 64 directories examined, not as a floor an implementation may exceed.  It is
# therefore a fixed contract value and the cases below test it as one.
WALK_UP_BOUND = 64


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def _case(root, name, metadata):
    directory = os.path.join(root, name)
    os.makedirs(os.path.join(directory, "project"), exist_ok=True)
    _write(os.path.join(directory, "case.json"), json.dumps(metadata, indent=2) + "\n")
    return os.path.join(directory, "project")


def repo_boundary_stop(root):
    """A version-control marker stops the upward search.

    Not committable: git will not track a nested directory named ``.git``, so a
    committed copy of this case would silently ship without the marker that is
    the entire point of it.
    """
    project = _case(
        root,
        "03-repo-boundary-stop",
        {
            "description": "A version-control marker stops the upward search, so a manifest above it does not capture the file.",
            "class": "loader",
            "subject": "a.qasm",
            "discover_from": "project/repo/a.qasm",
            "expect": {
                "canonical_names": ["a.qasm"],
                "root_canonical_name": "a.qasm",
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, "repo", ".git", "HEAD"), "ref: refs/heads/main\n")
    _write(os.path.join(project, "repo", "a.qasm"), "OPENQASM 3.0;\n")
    return True


def walk_stops_at_git_marker(root):
    """A version-control marker stops the downward file-set walk.

    Not committable, for the same reason as ``03-repo-boundary-stop``: git will
    not track a nested directory named ``.git``.  The committed
    ``63-walk-stops-at-repository-marker`` covers the same rule with ``.hg``, so
    that the marker set is established as more than git alone.
    """
    project = _case(
        root,
        "68-walk-stops-at-git-marker",
        {
            "description": "The default file walk does not descend into a directory that is a repository of its own, so a vendored checkout is not part of the project containing it.",
            "class": "loader",
            "subject": "main.qasm",
            "expect": {
                "canonical_names": ["main.qasm"],
                "root_canonical_name": "main.qasm",
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, "main.qasm"), "OPENQASM 3.0;\n")
    _write(os.path.join(project, "vendored", ".git", "HEAD"), "ref: refs/heads/main\n")
    _write(os.path.join(project, "vendored", "gates.inc"), "gate g q { U(0, 0, 0) q; }\n")
    return True


def depth_exceeded(root, ceiling):
    """A chain one deeper than the implementation supports.

    Not committable: the ceiling is implementation-defined above the specified
    minimum of 15, so a fixed tree would pin one implementation's choice.
    """
    depth = ceiling + 1
    project = _case(
        root,
        "08-depth-exceeded",
        {
            "description": "A chain one deeper than the implementation supports is diagnosed.",
            "class": "parser",
            "subject": "main.qasm",
            "generated_depth": depth,
            "expect": {"error": "include-depth-exceeded"},
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, "main.qasm"), 'OPENQASM 3.0;\ninclude "d001.inc";\n')
    for index in range(1, depth):
        _write(
            os.path.join(project, "d%03d.inc" % index),
            'include "d%03d.inc";\n' % (index + 1),
        )
    _write(os.path.join(project, "d%03d.inc" % depth), "gate deepest q { U(0, 0, 0) q; }\n")
    return True


def symlink_escape(root):
    """A symbolic link pointing outside the project root is not followed."""
    project = _case(
        root,
        "10-symlink-escape",
        {
            "description": "A symbolic link that leaves the project root is never traversed.",
            "class": "loader",
            "subject": "main.qasm",
            "expect": {
                "canonical_names": ["main.qasm"],
                "root_canonical_name": "main.qasm",
                "programs": None,
            },
        },
    )
    outside = os.path.join(os.path.dirname(os.path.dirname(project)), "outside")
    _write(os.path.join(outside, "secret.inc"), "gate secret q { U(0, 0, 0) q; }\n")
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, "main.qasm"), "OPENQASM 3.0;\n")
    try:
        os.symlink(outside, os.path.join(project, "escape"), target_is_directory=True)
    except (OSError, NotImplementedError, AttributeError):
        return False
    return True


def symlink_internal(root):
    """A symbolic link inside the project root is skipped by the walk."""
    project = _case(
        root,
        "11-symlink-internal",
        {
            "description": "A symbolic link inside the project root is skipped rather than followed, so its target is not incorporated twice.",
            "class": "loader",
            "subject": "main.qasm",
            "expect": {
                "canonical_names": ["main.qasm", "real/g.inc"],
                "root_canonical_name": "main.qasm",
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, "main.qasm"), "OPENQASM 3.0;\n")
    _write(os.path.join(project, "real", "g.inc"), "gate g q { U(0, 0, 0) q; }\n")
    try:
        os.symlink(
            os.path.join(project, "real"),
            os.path.join(project, "alias"),
            target_is_directory=True,
        )
    except (OSError, NotImplementedError, AttributeError):
        return False
    return True


def unicode_normalization(root):
    """A decomposed file name is the canonical name, unchanged.

    Not committable: version-control tooling on some platforms normalizes names
    as they are added, so committing this case would silently destroy the
    distinction it exists to test.
    """
    precomposed = unicodedata.normalize("NFC", "caf\u00e9.inc")
    decomposed = unicodedata.normalize("NFD", precomposed)
    project = _case(
        root,
        "20-unicode-normalization",
        {
            "description": "A name is used exactly as the volume stores it, so a decomposed file name is the canonical name rather than its precomposed form.",
            "class": "loader",
            "subject": decomposed,
            "expect": {
                "canonical_names": [decomposed],
                "root_canonical_name": decomposed,
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    _write(os.path.join(project, decomposed), "gate cafe q { U(0, 0, 0) q; }\n")
    # A volume that normalizes names on creation cannot host this case.
    if decomposed not in os.listdir(project):
        return False
    return True


def _nest(base, depth):
    """Return a directory ``depth`` levels below ``base``, creating it.

    Directory names are a single character so that a 64-deep tree stays well
    inside the path-length limits of every host the suite runs on.
    """
    directory = base
    for _ in range(depth):
        directory = os.path.join(directory, "d")
    os.makedirs(directory, exist_ok=True)
    return directory


def walk_up_bound_reached(root):
    """A manifest at the last directory the search examines is still found.

    Not committable: the tree is 63 directories deep, which is impractical to
    store and would dominate the repository's file count.
    """
    nested = "/".join("d" * (WALK_UP_BOUND - 1))
    # The subject sits at the bottom of the chain, so its project-relative source
    # name, and therefore its project-form canonical name, is the whole chain.
    # Derive it rather than writing it out, so the expectation cannot drift from
    # the tree.
    subject_name = "%s/main.qasm" % nested
    project = _case(
        root,
        "27-walk-up-bound-reached",
        {
            "description": "A manifest in the last directory the upward search examines is found, because the bound counts directories examined rather than parent steps taken.",
            "class": "loader",
            "subject": subject_name,
            "discover_from": "project/%s" % subject_name,
            "generated_depth": WALK_UP_BOUND - 1,
            "expect": {
                "canonical_names": [subject_name],
                "root_canonical_name": subject_name,
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    deepest = _nest(project, WALK_UP_BOUND - 1)
    _write(os.path.join(deepest, "main.qasm"), "OPENQASM 3.0;\n")
    return True


def walk_up_bound_exceeded(root):
    """A manifest one directory beyond the bound is not found.

    This is the case that distinguishes a conforming search from one that loops
    once too many times.  An implementation that examines 65 directories finds
    the manifest here and disagrees with every implementation that does not.
    """
    project = _case(
        root,
        "28-walk-up-bound-exceeded",
        {
            "description": "A manifest one directory beyond the bound is not found, and the subject is compiled in single-file mode.",
            "class": "loader",
            "subject": "main.qasm",
            "discover_from": "project/%s/main.qasm" % "/".join("d" * WALK_UP_BOUND),
            "generated_depth": WALK_UP_BOUND,
            "expect": {
                "canonical_names": ["main.qasm"],
                "root_canonical_name": "main.qasm",
                "programs": None,
            },
        },
    )
    _write(os.path.join(project, "openqasm.json"), "{}\n")
    deepest = _nest(project, WALK_UP_BOUND)
    _write(os.path.join(deepest, "main.qasm"), "OPENQASM 3.0;\n")
    return True


def containment_escape(root):
    """A declared file reached through an escaping symbolic link is refused.

    Not committable: it needs a symbolic link pointing outside the project root.
    """
    project = _case(
        root,
        "42-containment-escape",
        {
            "description": "A declared file that resolves outside the project root is refused.",
            "class": "loader",
            "expect": {"error": "containment-escape"},
        },
    )
    outside = os.path.join(os.path.dirname(os.path.dirname(project)), "outside")
    _write(os.path.join(outside, "secret.inc"), "gate secret q { U(0, 0, 0) q; }\n")
    _write(os.path.join(project, "openqasm.json"), '{"files": ["escape/secret.inc"]}\n')
    try:
        os.symlink(outside, os.path.join(project, "escape"), target_is_directory=True)
    except (OSError, NotImplementedError, AttributeError):
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="directory to materialize cases into")
    parser.add_argument(
        "--depth-ceiling",
        type=int,
        default=DEFAULT_DEPTH_CEILING,
        help="the inclusion depth the implementation under test supports",
    )
    arguments = parser.parse_args(argv)

    if arguments.depth_ceiling < 15:
        parser.error("an implementation must support an inclusion depth of at least 15")

    root = os.path.abspath(arguments.out)
    marker = os.path.join(root, MARKER_NAME)
    if os.path.exists(root):
        if not os.path.isdir(root):
            parser.error("--out names an existing file: %s" % root)
        if os.listdir(root) and not os.path.isfile(marker):
            parser.error(
                "refusing to erase %s: it is not empty and holds no %s, so this generator"
                " did not write it" % (root, MARKER_NAME)
            )
        shutil.rmtree(root)
    os.makedirs(root)
    with open(marker, "w", encoding="utf-8") as stream:
        stream.write(
            "Written by conformance/project/generated/generate.py.\n"
            "This directory is erased and rewritten on each run.\n"
        )

    results = [
        ("03-repo-boundary-stop", repo_boundary_stop(root)),
        ("08-depth-exceeded", depth_exceeded(root, arguments.depth_ceiling)),
        ("10-symlink-escape", symlink_escape(root)),
        ("11-symlink-internal", symlink_internal(root)),
        ("20-unicode-normalization", unicode_normalization(root)),
        ("27-walk-up-bound-reached", walk_up_bound_reached(root)),
        ("28-walk-up-bound-exceeded", walk_up_bound_exceeded(root)),
        ("42-containment-escape", containment_escape(root)),
        ("68-walk-stops-at-git-marker", walk_stops_at_git_marker(root)),
    ]

    for name, generated in results:
        if generated:
            print("generated %s" % name)
        else:
            shutil.rmtree(os.path.join(root, name), ignore_errors=True)
            print("skipped   %s (this host cannot host it)" % name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
