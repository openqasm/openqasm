"""Tests for :mod:`openqasm3.project`, including the conformance corpus."""

import importlib.util
import json
import os
import subprocess
import sys
import unicodedata
from dataclasses import FrozenInstanceError

import pytest

import openqasm3.project as project_module
from openqasm3.resolver import IncludeNotFoundError, STANDARD_LIBRARY_NAME
from openqasm3.project import (
    MANIFEST_NAME,
    MAX_WALK_UP_STEPS,
    CanonicalNameError,
    ContainmentError,
    FileSetError,
    LibraryError,
    LoadedProject,
    Manifest,
    ManifestError,
    ProjectError,
    canonical_name,
    collect_default_file_set,
    contained,
    discover,
    load_project,
    load_target,
    read_manifest,
)


_RAW_MANIFEST_TYPING_FIXTURE: Manifest = {
    "$schema": "https://openqasm.com/_static/schemas/openqasm-project-v1.schema.json",
    "futureKey": {"enabled": True},
    "libraries": {"v": {"path": "../vendor", "futureKey": 1}},
}
_RAW_MALFORMED_MANIFEST_TYPING_FIXTURE: Manifest = {"libraries": []}


def write(root, relative, text=""):
    path = os.path.join(str(root), *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def project(root, manifest="{}", files=None):
    """Create a project at ``root``.  ``files`` maps a relative path to its text."""
    write(root, MANIFEST_NAME, manifest)
    for relative, text in (files or {}).items():
        write(root, relative, text)
    return str(root)


class TestManifest:
    def test_empty_object_is_a_valid_manifest(self, tmp_path):
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        assert load_project(root).sources == {"main.qasm": "OPENQASM 3.0;"}

    def test_missing_manifest_is_treated_as_empty(self, tmp_path):
        write(tmp_path, "main.qasm", "OPENQASM 3.0;")
        assert set(load_project(str(tmp_path)).sources) == {"main.qasm"}

    def test_unknown_key_is_tolerated(self, tmp_path):
        root = project(tmp_path, '{"futureKey": 1}', {"main.qasm": "OPENQASM 3.0;"})
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_comment_key_is_tolerated(self, tmp_path):
        root = project(tmp_path, '{"$comment": "a note"}', {"main.qasm": "OPENQASM 3.0;"})
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_comment_value_must_be_a_string(self, tmp_path):
        root = project(tmp_path, '{"$comment": 1}', {"main.qasm": "OPENQASM 3.0;"})

        with pytest.raises(ManifestError, match="'\\$comment' must be a string"):
            load_project(root)

    def test_duplicate_key_is_rejected(self, tmp_path):
        root = project(tmp_path, '{"files": ["a.inc"], "files": []}', {"a.inc": ""})
        with pytest.raises(ManifestError, match="duplicate manifest key"):
            load_project(root)

    def test_nonstandard_constant_is_rejected(self, tmp_path):
        root = project(tmp_path, '{"version": NaN}')
        with pytest.raises(ManifestError, match="non-JSON constant"):
            load_project(root)

    @pytest.mark.parametrize("magnitude", [2**53, -(2**53), 2**64])
    def test_an_integer_too_large_for_a_double_is_rejected(self, tmp_path, magnitude):
        root = project(tmp_path, '{"futureKey": %d}' % magnitude)
        with pytest.raises(ManifestError) as caught:
            load_project(root)
        assert caught.value.identity == "manifest-integer-too-large"

    def test_the_largest_exactly_representable_integer_is_accepted(self, tmp_path):
        root = project(tmp_path, '{"futureKey": %d}' % (2**53 - 1), {"main.qasm": "OPENQASM 3.0;"})
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_the_magnitude_rule_reaches_a_key_the_loader_ignores(self, tmp_path):
        # A value ignored today is one a later loader reads, so the check cannot wait for
        # the key to be recognized.
        root = project(tmp_path, '{"nested": {"deep": [1, %d]}}' % 2**53)
        with pytest.raises(ManifestError) as caught:
            load_project(root)
        assert caught.value.identity == "manifest-integer-too-large"

    def test_a_comment_in_libraries_is_a_library_rather_than_a_note(self, tmp_path):
        # Its keys are names its author chooses, so nothing there can be an annotation.
        root = project(tmp_path, '{"libraries": {"$comment": "a note"}}')
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-declaration-invalid"

    def test_a_comment_inside_one_library_is_tolerated(self, tmp_path):
        write(tmp_path, "app/main.qasm", "OPENQASM 3.0;")
        write(tmp_path, "vendor/gates.inc", "gate g q { U(0, 0, 0) q; }")
        write(tmp_path, "vendor/" + MANIFEST_NAME, '{"name": "vendor"}')
        write(
            tmp_path,
            "app/" + MANIFEST_NAME,
            '{"libraries": {"v": {"path": "../vendor", "$comment": "why we use it"}}}',
        )
        loaded = load_project(str(tmp_path / "app"))
        assert sorted(loaded.sources) == ["@vendor/gates.inc", "main.qasm"]

    def test_a_comment_inside_one_library_must_be_a_string(self, tmp_path):
        write(tmp_path, "app/main.qasm", "OPENQASM 3.0;")
        write(tmp_path, "vendor/gates.inc", "gate g q { U(0, 0, 0) q; }")
        write(tmp_path, "vendor/" + MANIFEST_NAME, '{"name": "vendor"}')
        write(
            tmp_path,
            "app/" + MANIFEST_NAME,
            '{"libraries": {"v": {"path": "../vendor", "$comment": 1}}}',
        )

        with pytest.raises(LibraryError) as caught:
            load_project(str(tmp_path / "app"))

        assert caught.value.identity == "library-declaration-invalid"

    @pytest.mark.parametrize("stem", ["notes[1]", "gates{v2}", "q[0]"])
    def test_a_name_holding_a_bracket_or_brace_is_a_name_not_a_pattern(self, tmp_path, stem):
        # These are legal characters on every volume, and the walk feeds real file names
        # through the same validator a declared entry passes.
        root = project(tmp_path, "{}", {stem + ".inc": "gate g q { U(0, 0, 0) q; }"})
        assert set(load_project(root).sources) == {stem + ".inc"}

    @pytest.mark.parametrize("entry", ["lib/*.inc", "gates?.inc"])
    def test_a_glob_metacharacter_is_still_refused(self, tmp_path, entry):
        root = project(tmp_path, json.dumps({"files": [entry]}))
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "files-name-invalid"

    def test_a_declared_symbolic_link_is_refused(self, tmp_path):
        # The walk skips links so that one file cannot take two canonical names; an
        # explicit list has to diagnose what it cannot honor rather than drop it.
        write(tmp_path, "real.inc", "gate g q { U(0, 0, 0) q; }")
        try:
            os.symlink(str(tmp_path / "real.inc"), str(tmp_path / "alias.inc"))
        except (OSError, NotImplementedError, AttributeError):
            pytest.skip("this host cannot create a symbolic link")
        write(tmp_path, MANIFEST_NAME, json.dumps({"files": ["real.inc", "alias.inc"]}))
        with pytest.raises(FileSetError) as caught:
            load_project(str(tmp_path))
        assert caught.value.identity == "files-symbolic-link"

    def test_byte_order_mark_is_rejected(self, tmp_path):
        path = write(tmp_path, MANIFEST_NAME)
        with open(path, "w", encoding="utf-8-sig") as stream:
            stream.write("{}")
        with pytest.raises(ManifestError, match="byte-order mark"):
            read_manifest(path)

    def test_invalid_utf8_is_rejected_as_a_manifest_error(self, tmp_path):
        path = tmp_path / MANIFEST_NAME
        path.write_bytes(b"{\xff}")
        with pytest.raises(ManifestError, match="must be UTF-8"):
            read_manifest(path)

    def test_malformed_json_is_rejected(self, tmp_path):
        root = project(tmp_path, "{not json")
        with pytest.raises(ManifestError, match="not valid JSON"):
            load_project(root)

    def test_non_object_root_is_rejected(self, tmp_path):
        root = project(tmp_path, "[]")
        with pytest.raises(ManifestError, match="must hold a JSON object"):
            load_project(root)

    def test_read_manifest_preserves_open_extension_data(self, tmp_path):
        path = write(tmp_path, MANIFEST_NAME, json.dumps(_RAW_MANIFEST_TYPING_FIXTURE))

        assert read_manifest(path) == _RAW_MANIFEST_TYPING_FIXTURE

    @pytest.mark.parametrize(
        ("manifest", "identity"),
        [
            ({"name": 42}, "library-declaration-invalid"),
            ({"files": "main.qasm"}, "files-declaration-invalid"),
            ({"programs": "main.qasm"}, "programs-declaration-invalid"),
            (_RAW_MALFORMED_MANIFEST_TYPING_FIXTURE, "library-declaration-invalid"),
        ],
        ids=["name", "files", "programs", "libraries"],
    )
    def test_recognized_fields_are_raw_until_semantic_loading(self, tmp_path, manifest, identity):
        path = write(tmp_path, MANIFEST_NAME, json.dumps(manifest))
        parsed = read_manifest(path)

        assert parsed == manifest
        with pytest.raises(ProjectError) as caught:
            load_project(str(tmp_path), manifest=parsed)
        assert caught.value.identity == identity

    def test_files_must_be_an_array_of_strings(self, tmp_path):
        root = project(tmp_path, '{"files": "main.qasm"}')
        with pytest.raises(ManifestError, match="must be an array of strings"):
            load_project(root)


class TestFileSet:
    def test_explicit_list_is_exhaustive(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["main.qasm", "lib/listed.inc"]}',
            {
                "main.qasm": "OPENQASM 3.0;",
                "lib/listed.inc": "listed",
                "lib/unlisted.inc": "unlisted",
            },
        )
        assert set(load_project(root).sources) == {"main.qasm", "lib/listed.inc"}

    def test_default_walk_collects_sources_only(self, tmp_path):
        root = project(
            tmp_path,
            files={
                "main.qasm": "OPENQASM 3.0;",
                "lib/b.inc": "b",
                "notes.txt": "not a source",
            },
        )
        assert set(load_project(root).sources) == {"main.qasm", "lib/b.inc"}

    def test_default_walk_skips_hidden_entries(self, tmp_path):
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        write(tmp_path, ".hidden.inc", "hidden")
        write(tmp_path, ".hidden-dir/nested.inc", "nested")
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_default_walk_is_sorted_by_utf8_bytes(self, tmp_path):
        root = project(tmp_path)
        for name in ("b.inc", "a.inc", "Z.inc", "\u00e9.inc"):
            write(tmp_path, name, "")
        collected = collect_default_file_set(root)
        assert collected == tuple(sorted(collected, key=lambda name: name.encode("utf-8")))
        assert collected[0] == "Z.inc"

    def test_default_walk_stops_at_a_nested_manifest(self, tmp_path):
        """Reproduced: the enclosing project absorbed a nested project's files."""
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        project(tmp_path / "nested", files={"inner.inc": "inner"})
        assert set(load_project(root).sources) == {"main.qasm"}

    @pytest.mark.parametrize("marker", [".git", ".hg", ".svn", ".jj"])
    def test_default_walk_stops_at_a_repository_marker(self, tmp_path, marker):
        """A vendored checkout is a repository of its own, whatever marker it carries."""
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        write(tmp_path, "vendored/%s/HEAD" % marker, "")
        write(tmp_path, "vendored/theirs.inc", "theirs")
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_a_repository_marker_that_is_a_file_also_stops_the_walk(self, tmp_path):
        """A worktree or submodule records '.git' as a file rather than a directory."""
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        write(tmp_path, "worktree/.git", "gitdir: ../.git/worktrees/w\n")
        write(tmp_path, "worktree/theirs.inc", "theirs")
        assert set(load_project(root).sources) == {"main.qasm"}

    def test_the_root_manifest_does_not_end_the_root_walk(self, tmp_path):
        """The boundary applies to nested directories, never to the project being loaded."""
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;", "lib/b.inc": "b"})
        assert set(load_project(root).sources) == {"main.qasm", "lib/b.inc"}

    def test_extension_match_is_case_sensitive(self, tmp_path):
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        write(tmp_path, "SHOUTY.INC", "")
        assert set(load_project(root).sources) == {"main.qasm"}

    @pytest.mark.parametrize(
        "entry",
        [
            "/absolute.inc",
            "\\leading-backslash.inc",
            "lib\\gates.inc",
            "C:/drive.inc",
            "../escape.inc",
            "./here.inc",
            "lib//double.inc",
            "**/*.inc",
            "lib/{a,b}.inc",
            "lib/[ab].inc",
            "lib/a?.inc",
            "",
        ],
    )
    def test_invalid_names_are_rejected(self, tmp_path, entry):
        root = project(tmp_path, json.dumps({"files": [entry]}))
        with pytest.raises(FileSetError):
            load_project(root)

    def test_missing_file_is_rejected(self, tmp_path):
        root = project(tmp_path, '{"files": ["absent.inc"]}')
        with pytest.raises(FileSetError, match="does not exist"):
            load_project(root)

    def test_invalid_utf8_source_is_rejected_as_a_file_set_error(self, tmp_path):
        root = project(tmp_path, '{"files": ["bad.inc"]}')
        (tmp_path / "bad.inc").write_bytes(b"\xff")
        with pytest.raises(FileSetError, match="not UTF-8"):
            load_project(root)


class TestPrograms:
    def test_declared_names_are_reported_in_order(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm", "b.qasm"], "programs": ["b.qasm", "a.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;", "b.qasm": "OPENQASM 3.0;"},
        )
        assert load_project(root).programs == ("b.qasm", "a.qasm")

    def test_a_repeated_entry_is_rejected(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": ["a.qasm", "a.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "programs-name-duplicate"

    def test_membership_is_checked_against_the_default_walk(self, tmp_path):
        root = project(
            tmp_path,
            '{"programs": ["main.qasm"]}',
            {"main.qasm": "OPENQASM 3.0;", "lib/helper.inc": ""},
        )
        assert load_project(root).programs == ("main.qasm",)

    def test_an_unknown_name_is_rejected_against_the_default_walk(self, tmp_path):
        root = project(tmp_path, '{"programs": ["absent.qasm"]}', {"main.qasm": "OPENQASM 3.0;"})
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "programs-name-unknown"

    def test_a_nested_name_is_accepted(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["lib/main.qasm"], "programs": ["lib/main.qasm"]}',
            {"lib/main.qasm": "OPENQASM 3.0;"},
        )
        assert load_project(root).programs == ("lib/main.qasm",)

    def test_an_empty_array_differs_from_an_absent_key(self, tmp_path):
        declared = project(
            tmp_path / "declared",
            '{"files": ["a.qasm"], "programs": []}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        absent = project(tmp_path / "absent", '{"files": ["a.qasm"]}', {"a.qasm": "OPENQASM 3.0;"})
        assert load_project(declared).programs == ()
        assert load_project(absent).programs is None

    def test_an_unknown_name_is_rejected(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": ["absent.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "programs-name-unknown"

    def test_a_name_differing_only_by_case_is_unknown(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": ["A.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "programs-name-unknown"

    def test_an_invalid_name_blames_the_right_key(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": ["/a.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError, match="^programs entry") as caught:
            load_project(root)
        assert caught.value.identity == "files-name-invalid"

    @pytest.mark.parametrize("declared", ['"a.qasm"', "{}", "[1]"])
    def test_a_wrong_typed_value_is_rejected(self, tmp_path, declared):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": %s}' % declared,
            {"a.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(ManifestError, match="array of strings") as caught:
            load_project(root)
        # Named, matching the 'files' type check it follows.
        assert caught.value.identity == "programs-declaration-invalid"

    def test_a_decomposed_name_does_not_match_its_composed_file(self, tmp_path):
        composed = unicodedata.normalize("NFC", "caf\u00e9.qasm")
        decomposed = unicodedata.normalize("NFD", "caf\u00e9.qasm")
        root = project(
            tmp_path,
            json.dumps({"files": [composed], "programs": [decomposed]}),
            {composed: "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "programs-name-unknown"

    def test_the_result_is_structured(self, tmp_path):
        root = project(
            tmp_path,
            '{"files": ["a.qasm"], "programs": ["a.qasm"]}',
            {"a.qasm": "OPENQASM 3.0;"},
        )
        loaded = load_project(root)
        assert isinstance(loaded, LoadedProject)
        assert loaded.sources == {"a.qasm": "OPENQASM 3.0;"}


class TestCanonicalNames:
    @pytest.mark.parametrize("value", ["../escape.qasm", "/absolute.qasm", "lib\\gate.inc"])
    def test_construction_rejects_non_project_relative_source_names(self, value):
        with pytest.raises(FileSetError):
            canonical_name(value)

    def test_names_are_project_relative_posix(self, tmp_path):
        root = project(tmp_path, files={"lib/gates/extra.inc": "extra"})
        assert set(load_project(root).sources) == {"lib/gates/extra.inc"}

    @pytest.mark.parametrize("form", ["NFC", "NFD"])
    def test_names_are_used_exactly_as_given(self, form):
        name = unicodedata.normalize(form, "caf\u00e9.inc")
        assert canonical_name(name) == name

    def test_non_letter_colon_prefix_is_not_drive_qualified(self):
        assert canonical_name("1:/gate.inc") == "1:/gate.inc"

    def test_reserved_name_is_rejected(self, tmp_path):
        root = project(tmp_path, files={"stdgates.inc": "gate impostor q { U(0, 0, 0) q; }"})
        with pytest.raises(CanonicalNameError, match="reserved canonical name"):
            load_project(root)

    def test_reserved_name_only_applies_at_the_root(self, tmp_path):
        root = project(tmp_path, files={"lib/stdgates.inc": "gate local q { U(0, 0, 0) q; }"})
        assert set(load_project(root).sources) == {"lib/stdgates.inc"}

    def test_duplicate_name_is_rejected(self, tmp_path):
        root = project(tmp_path, '{"files": ["a.inc", "a.inc"]}', {"a.inc": ""})
        with pytest.raises(CanonicalNameError, match="duplicate canonical name"):
            load_project(root)

    def test_case_only_collision_is_rejected(self, tmp_path):
        root = project(tmp_path, '{"files": ["lib/Gates.inc", "lib/gates.inc"]}')
        write(tmp_path, "lib/gates.inc", "")
        write(tmp_path, "lib/Gates.inc", "")
        with pytest.raises(CanonicalNameError, match="differ only by case"):
            load_project(root)

    def test_a_character_that_would_normalize_to_an_ascii_letter_does_not_collide(self, tmp_path):
        # Nothing is normalized, so the Kelvin sign never becomes "K".
        root = project(tmp_path, '{"files": ["k.inc", "\u212a.inc"]}')
        write(tmp_path, "k.inc", "")
        write(tmp_path, "\u212a.inc", "")
        assert set(load_project(root).sources) == {"k.inc", "\u212a.inc"}

    def test_a_name_fault_is_decided_before_any_file_is_opened(self, tmp_path):
        # Otherwise a case-insensitive volume reports the collision and a case-sensitive one
        # reports the missing file, for one project that neither can load.
        root = project(tmp_path, json.dumps({"files": ["absent.qasm", "a.inc", "A.inc"]}))
        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)
        assert caught.value.identity == "canonical-name-case-collision"

    def test_names_differing_only_by_normalization_collide(self, tmp_path):
        # A Linux volume holds both, and the loader is the only layer that can name the two
        # files; the resolver would only report an ambiguity at the first include of either.
        composed = "caf\u00e9.inc"
        decomposed = "cafe\u0301.inc"
        root = project(tmp_path, json.dumps({"files": [composed, decomposed]}))
        write(tmp_path, composed, "")
        write(tmp_path, decomposed, "")
        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)
        assert caught.value.identity == "canonical-name-normalization-collision"

    def test_non_ascii_case_is_not_a_collision(self, tmp_path):
        root = project(tmp_path, '{"files": ["\u03c3.inc", "\u03a3.inc"]}')
        write(tmp_path, "\u03c3.inc", "")
        write(tmp_path, "\u03a3.inc", "")
        assert set(load_project(root).sources) == {"\u03c3.inc", "\u03a3.inc"}


class TestContainment:
    def test_a_prefix_match_is_not_containment(self, tmp_path):
        inside = tmp_path / "a"
        sibling = tmp_path / "ab"
        inside.mkdir()
        sibling.mkdir()
        assert not contained(str(sibling / "c.inc"), str(inside))

    def test_a_directory_contains_itself(self, tmp_path):
        assert contained(str(tmp_path), str(tmp_path))

    def test_a_missing_path_is_still_testable(self, tmp_path):
        assert contained(str(tmp_path / "absent" / "x.inc"), str(tmp_path))

    @pytest.mark.skipif(not hasattr(os, "symlink"), reason="host has no symbolic links")
    def test_symlink_escape_is_refused(self, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.inc").write_text("secret", encoding="utf-8")
        root = tmp_path / "project"
        root.mkdir()
        try:
            os.symlink(str(outside), str(root / "escape"), target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("host cannot create symbolic links")
        assert not contained(str(root / "escape" / "secret.inc"), str(root))

    @pytest.mark.skipif(not hasattr(os, "symlink"), reason="host has no symbolic links")
    def test_a_listed_file_reached_through_an_escaping_link_is_refused(self, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.inc").write_text("secret", encoding="utf-8")
        root = tmp_path / "project"
        root.mkdir()
        write(root, MANIFEST_NAME, '{"files": ["escape/secret.inc"]}')
        try:
            os.symlink(str(outside), str(root / "escape"), target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("host cannot create symbolic links")
        with pytest.raises(ContainmentError, match="escapes the root that supplies it"):
            load_project(str(root))

    @pytest.mark.skipif(not hasattr(os, "symlink"), reason="host has no symbolic links")
    def test_walk_does_not_follow_symlinks(self, tmp_path):
        root = project(tmp_path, files={"real/g.inc": "gate g q { U(0, 0, 0) q; }"})
        try:
            os.symlink(
                os.path.join(str(tmp_path), "real"),
                os.path.join(str(tmp_path), "alias"),
                target_is_directory=True,
            )
        except (OSError, NotImplementedError):
            pytest.skip("host cannot create symbolic links")
        assert set(load_project(root).sources) == {"real/g.inc"}


class TestDiscovery:
    def test_manifest_in_the_same_directory_is_found(self, tmp_path):
        root = project(tmp_path, files={"main.qasm": "OPENQASM 3.0;"})
        assert discover(os.path.join(root, "main.qasm")) == str(tmp_path)

    def test_search_walks_upwards(self, tmp_path):
        root = project(tmp_path)
        write(tmp_path, "a/b/c/main.qasm", "OPENQASM 3.0;")
        assert discover(os.path.join(root, "a", "b", "c", "main.qasm")) == str(tmp_path)

    def test_nearest_manifest_wins(self, tmp_path):
        project(tmp_path)
        inner = tmp_path / "inner"
        inner.mkdir()
        write(inner, MANIFEST_NAME, "{}")
        write(inner, "main.qasm", "OPENQASM 3.0;")
        assert discover(os.path.join(str(inner), "main.qasm")) == str(inner)

    def test_no_manifest_means_no_project(self, tmp_path):
        write(tmp_path, "a/main.qasm", "OPENQASM 3.0;")
        found = discover(os.path.join(str(tmp_path), "a", "main.qasm"), home_dir=str(tmp_path))
        assert found is None

    @pytest.mark.parametrize("marker", [".git", ".hg", ".svn", ".jj"])
    def test_repository_marker_stops_the_search(self, tmp_path, marker):
        project(tmp_path)
        repo = tmp_path / "repo"
        (repo / marker).mkdir(parents=True)
        write(repo, "main.qasm", "OPENQASM 3.0;")
        assert discover(os.path.join(str(repo), "main.qasm")) is None

    def test_manifest_beats_a_marker_in_the_same_directory(self, tmp_path):
        root = project(tmp_path)
        (tmp_path / ".git").mkdir()
        write(tmp_path, "main.qasm", "OPENQASM 3.0;")
        assert discover(os.path.join(root, "main.qasm")) == str(tmp_path)

    def test_home_directory_stops_the_search(self, tmp_path):
        project(tmp_path)
        nested = tmp_path / "nested"
        nested.mkdir()
        write(nested, "main.qasm", "OPENQASM 3.0;")
        found = discover(os.path.join(str(nested), "main.qasm"), home_dir=str(nested))
        assert found is None

    def test_home_directory_comparison_uses_filesystem_case_rules(self, tmp_path, monkeypatch):
        project(tmp_path)
        home = tmp_path / "Home"
        work = home / "work"
        work.mkdir(parents=True)
        write(work, "main.qasm", "OPENQASM 3.0;")
        monkeypatch.setattr(os.path, "normcase", str.lower)
        found = discover(os.path.join(str(work), "main.qasm"), home_dir=str(home).lower())
        assert found is None

    def test_workspace_roots_stop_the_search(self, tmp_path):
        project(tmp_path)
        work = tmp_path / "work"
        work.mkdir()
        write(work, "main.qasm", "OPENQASM 3.0;")
        found = discover(os.path.join(str(work), "main.qasm"), workspace_roots=[str(work)])
        assert found is None

    def test_a_broken_manifest_stops_the_search_rather_than_continuing(self, tmp_path):
        project(tmp_path)
        inner = tmp_path / "inner"
        inner.mkdir()
        write(inner, MANIFEST_NAME, "{oops")
        write(inner, "main.qasm", "OPENQASM 3.0;")
        root = discover(os.path.join(str(inner), "main.qasm"))
        assert root == str(inner)
        with pytest.raises(ManifestError):
            load_project(root)

    def test_a_manifest_at_the_bound_is_found(self, tmp_path):
        """MAX_WALK_UP_STEPS counts directories examined, so the last one counts."""
        deepest = self._nest(tmp_path, MAX_WALK_UP_STEPS - 1)
        write(tmp_path, MANIFEST_NAME, "{}")
        write(deepest, "main.qasm", "OPENQASM 3.0;")
        found = discover(os.path.join(deepest, "main.qasm"), home_dir=str(tmp_path.parent))
        assert found == str(tmp_path)

    def test_a_manifest_one_past_the_bound_is_not_found(self, tmp_path):
        """The bound is the specified stop condition, not an approximation of one."""
        deepest = self._nest(tmp_path, MAX_WALK_UP_STEPS)
        write(tmp_path, MANIFEST_NAME, "{}")
        write(deepest, "main.qasm", "OPENQASM 3.0;")
        found = discover(os.path.join(deepest, "main.qasm"), home_dir=str(tmp_path.parent))
        assert found is None

    @staticmethod
    def _nest(root, depth):
        """Return a directory ``depth`` levels below ``root``."""
        directory = str(root)
        for index in range(depth):
            directory = os.path.join(directory, "d%02d" % index)
        os.makedirs(directory, exist_ok=True)
        return directory


class TestLoadTarget:
    def test_manifest_backed_target_loads_project_and_returns_canonical_name(self, tmp_path):
        root = project(
            tmp_path,
            manifest=json.dumps(
                {
                    "files": ["programs/main.qasm", "lib/gates.inc"],
                    "programs": ["programs/main.qasm"],
                }
            ),
            files={
                "programs/main.qasm": 'OPENQASM 3.0;\ninclude "../lib/gates.inc";',
                "lib/gates.inc": "gate g q { U(0, 0, 0) q; }",
            },
        )

        loaded = project_module.load_target(os.path.join(root, "programs", "main.qasm"))
        name = loaded.compilation_root

        assert name == "programs/main.qasm"
        assert name in loaded.sources
        assert loaded.programs == ("programs/main.qasm",)

    def test_manifest_free_target_loads_only_the_selected_file(self, tmp_path):
        target = write(tmp_path, "nested/main.qasm", "OPENQASM 3.0;")
        write(tmp_path, "nested/sibling.inc", "gate g q { U(0, 0, 0) q; }")

        loaded = project_module.load_target(target, home_dir=str(tmp_path))
        name = loaded.compilation_root

        assert name == "main.qasm"
        assert loaded.sources == {"main.qasm": "OPENQASM 3.0;"}
        assert loaded.programs is None

    @pytest.mark.parametrize("target_kind", ["missing", "directory"])
    def test_non_file_target_is_refused(self, tmp_path, target_kind):
        target = tmp_path / "target"
        if target_kind == "directory":
            target.mkdir()

        with pytest.raises(FileSetError):
            project_module.load_target(target)

    def test_target_excluded_from_discovered_file_set_is_refused(self, tmp_path):
        root = project(
            tmp_path,
            manifest=json.dumps({"files": ["included.inc"]}),
            files={
                "included.inc": "gate g q { U(0, 0, 0) q; }",
                "excluded.qasm": "OPENQASM 3.0;",
            },
        )

        with pytest.raises(FileSetError):
            project_module.load_target(os.path.join(root, "excluded.qasm"))


class TestParserIntegration:
    """The loaded project is the parser's coherent resolution input."""

    def test_mapping_drives_the_parser(self, tmp_path):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        pytest.importorskip("antlr4", reason="needs the [parser] extra")
        root = project(
            tmp_path,
            files={
                "main.qasm": 'OPENQASM 3.0;\ninclude "lib/gates/extra.inc";',
                "lib/gates/extra.inc": 'include "helpers.inc";',
                "lib/gates/helpers.inc": "gate helper q { U(0, 0, 0) q; }",
            },
        )
        loaded = load_project(root)
        program = openqasm3.parse_project(loaded, "main.qasm")
        names = [unit.canonical_name for unit in program.sources]
        assert names == ["main.qasm", "lib/gates/extra.inc", "lib/gates/helpers.inc"]

    def test_a_lone_reserved_name_loads_as_a_compilation_root(self, tmp_path):
        """Reproduced: opening a file called stdgates.inc refused to load it at all."""
        write(tmp_path, STANDARD_LIBRARY_NAME, "gate g q { U(0, 0, 0) q; }\n")
        loaded = load_target(tmp_path / STANDARD_LIBRARY_NAME)
        name = loaded.compilation_root
        assert name == STANDARD_LIBRARY_NAME
        assert set(loaded.sources) == {STANDARD_LIBRARY_NAME}

    def test_a_reserved_name_inside_a_project_loads_when_it_is_the_target(self, tmp_path):
        root = project(
            tmp_path,
            files={
                "main.qasm": "OPENQASM 3.0;",
                STANDARD_LIBRARY_NAME: "gate g q { U(0, 0, 0) q; }\n",
            },
        )
        loaded = load_target(os.path.join(root, STANDARD_LIBRARY_NAME))
        name = loaded.compilation_root
        assert name == STANDARD_LIBRARY_NAME
        assert set(loaded.sources) == {"main.qasm", STANDARD_LIBRARY_NAME}

    def test_a_non_root_project_file_may_not_take_the_reserved_name(self, tmp_path):
        """The rule still holds for a file nothing selected, which no include could reach."""
        root = project(
            tmp_path,
            files={
                "main.qasm": "OPENQASM 3.0;",
                STANDARD_LIBRARY_NAME: "gate g q { U(0, 0, 0) q; }\n",
            },
        )
        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)
        assert caught.value.identity == "canonical-name-reserved"

        # Selecting a different file in the same project is equally not an exemption.
        with pytest.raises(CanonicalNameError) as caught:
            load_target(os.path.join(root, "main.qasm"))
        assert caught.value.identity == "canonical-name-reserved"

    def test_reserved_name_still_reaches_the_standard_library(self, tmp_path):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        pytest.importorskip("antlr4", reason="needs the [parser] extra")
        root = project(
            tmp_path,
            files={
                "main.qasm": 'OPENQASM 3.0;\ninclude "stdgates.inc";',
                "lib/stdgates.inc": "gate local q { U(0, 0, 0) q; }",
            },
        )
        loaded = load_project(root)
        program = openqasm3.parse_project(loaded, "main.qasm")
        names = [unit.canonical_name for unit in program.sources]
        assert names == ["main.qasm", "stdgates.inc"]
        # The project's own lib/stdgates.inc was not what the bare target reached.
        assert program.sources[1].statements == []


def _corpus_root():
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.abspath(os.path.join(here, "..", "..", "..", "conformance", "project"))
    return candidate if os.path.isdir(os.path.join(candidate, "cases")) else None


CORPUS = _corpus_root()

corpus_required = pytest.mark.skipif(
    CORPUS is None,
    reason=(
        "the conformance corpus lives at the repository root and is not shipped"
        " inside the package, so it is unavailable when tests run against an"
        " installed distribution"
    ),
)


def _schema_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.abspath(
        os.path.join(here, "..", "..", "_static", "schemas", "openqasm-project-v1.schema.json")
    )
    return candidate if os.path.isfile(candidate) else None


SCHEMA_PATH = _schema_path()

schema_required = pytest.mark.skipif(
    SCHEMA_PATH is None or CORPUS is None,
    reason=(
        "the published schema and the conformance corpus both live in the"
        " repository rather than in the package, so neither is available when"
        " tests run against an installed distribution"
    ),
)


def _corpus_manifests():
    """Every ``openqasm.json`` in the corpus, keyed by the case that owns it."""
    if CORPUS is None:
        return []
    cases = os.path.join(CORPUS, "cases")
    found = []
    for directory, _subdirectories, names in os.walk(cases):
        if MANIFEST_NAME in names:
            case = os.path.relpath(directory, cases).split(os.sep)[0]
            found.append((case, os.path.join(directory, MANIFEST_NAME)))
    return sorted(found)


def _load_harness():
    """Load the corpus harness by path.

    The harness is the corpus's single interpretation of a case.  These tests
    drive it rather than reading ``case.json`` themselves, so that a case cannot
    mean one thing here and another thing to a runner.  It is not importable as
    a package because the corpus deliberately sits outside the distribution.
    """
    if CORPUS is None:
        return None
    spec = importlib.util.spec_from_file_location(
        "openqasm_conformance_harness", os.path.join(CORPUS, "harness.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HARNESS = _load_harness()


class TestConformanceHarness:
    def test_runner_command_uses_the_windows_command_processor(self):
        command = r'C:\Python313\python.exe "C:\OpenQASM Tests\runner.py"'
        processor = r"C:\Windows\System32\cmd.exe"
        assert HARNESS._runner_command(command, platform="nt", command_processor=processor) == [
            processor,
            "/d",
            "/s",
            "/c",
            command,
        ]

    def test_runner_command_uses_posix_shell_tokenization(self):
        assert HARNESS._runner_command("python 'runner with spaces.py'", platform="posix") == [
            "python",
            "runner with spaces.py",
        ]

    @pytest.mark.parametrize("platform", ["nt", "posix"])
    def test_runner_command_rejects_empty_input(self, platform):
        assert HARNESS._runner_command("  ", platform=platform) == []


def _corpus_case_names():
    """Every case the harness will report on, committed and generated."""
    if CORPUS is None:
        return []
    cases = os.path.join(CORPUS, "cases")
    committed = [
        name for name in os.listdir(cases) if os.path.isfile(os.path.join(cases, name, "case.json"))
    ]
    return sorted(committed + HARNESS.expected_generated_names())


@pytest.fixture(name="corpus_results", scope="module")
def fixture_corpus_results(tmp_path_factory):
    """Run the whole corpus once and key the outcomes by case name."""
    from openqasm3 import resolver

    runner = os.path.join(CORPUS, "runners", "python", "runner.py")
    out = str(tmp_path_factory.mktemp("conformance") / "generated")
    summary = HARNESS.run_corpus([sys.executable, runner], out, resolver.DEFAULT_MAX_INCLUDE_DEPTH)
    return {entry["case"]: entry for entry in summary["cases"]}


@corpus_required
class TestConformanceCorpus:
    """Runs the shared cross-implementation corpus through its harness.

    The reference runner is driven exactly as a runner in any other language
    would be, through the process contract, so these tests exercise the contract
    as well as the loader.  A case that the runner declines, because it does not
    implement the case class, is a skip rather than a pass, and so is a generated
    case this host cannot materialize.
    """

    @pytest.mark.parametrize("case_name", _corpus_case_names())
    def test_case(self, case_name, corpus_results):
        outcome = corpus_results[case_name]
        if outcome["outcome"] == HARNESS.SKIP:
            pytest.skip(outcome["reason"])
        assert outcome["outcome"] == HARNESS.PASS, outcome.get("reason")

    def test_every_case_declares_a_class_and_an_expectation(self):
        cases = os.path.join(CORPUS, "cases")
        for case_name in sorted(os.listdir(cases)):
            path = os.path.join(cases, case_name, "case.json")
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as stream:
                case = json.load(stream)
            assert case["class"] in ("loader", "parser", "derivation"), case_name
            assert "description" in case, case_name
            keys = set(case["expect"])
            assert (
                len(keys & {"canonical_names", "sources", "derived_programs", "error"}) == 1
            ), case_name

    def test_generator_refuses_a_ceiling_below_the_specified_minimum(self, tmp_path):
        generator = os.path.join(CORPUS, "generated", "generate.py")
        result = subprocess.run(
            [sys.executable, generator, "--out", str(tmp_path / "out"), "--depth-ceiling", "14"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0


@schema_required
class TestManifestSchema:
    """Checks the published editor schema against the corpus the loader answers.

    The schema is an aid to whoever writes a manifest, and the loader remains the
    reference: where they disagree the loader is right.  It is checked here
    because it was previously kept in step by hand, and a schema that has
    silently drifted misleads exactly the authors it exists to help.
    """

    # The manifests the schema is expected to reject, each with the loader
    # identity the case exists to provoke.  A rejection outside this set is a
    # schema that refuses a manifest the loader accepts.  A case that leaves the
    # set is a check the schema has quietly stopped making.
    REJECTED = {
        "32-programs-name-invalid": "files-name-invalid",
        "36-programs-name-duplicate": "programs-name-duplicate",
        "39-manifest-json-invalid": "manifest-json-invalid",
        "40-canonical-name-duplicate": "canonical-name-duplicate",
        "55-library-prefix-reserved": "files-name-invalid",
        "71-libraries-not-an-object": "library-declaration-invalid",
        "72-library-declared-as-a-string": "library-declaration-invalid",
        "73-library-path-absolute": "library-declaration-invalid",
    }

    @staticmethod
    def _validator():
        jsonschema = pytest.importorskip("jsonschema")
        with open(SCHEMA_PATH, encoding="utf-8") as stream:
            schema = json.load(stream)
        jsonschema.Draft7Validator.check_schema(schema)
        return jsonschema.Draft7Validator(schema)

    def test_the_schema_is_a_valid_draft_7_schema(self):
        assert self._validator() is not None

    def test_the_schema_rejects_exactly_the_manifests_the_corpus_rejects(self):
        validator = self._validator()
        rejected = {}
        for case, path in _corpus_manifests():
            try:
                with open(path, encoding="utf-8") as stream:
                    document = json.load(stream)
            except ValueError:
                # A manifest the corpus intends to be unparseable is outside the
                # schema's reach, and the loader diagnoses it before validation.
                rejected[case] = "unparseable"
                continue
            errors = list(validator.iter_errors(document))
            if errors:
                rejected[case] = errors[0].message
        assert sorted(rejected) == sorted(self.REJECTED), rejected

    def test_every_rejection_belongs_to_a_case_that_expects_an_error(self):
        for case, identity in self.REJECTED.items():
            with open(os.path.join(CORPUS, "cases", case, "case.json"), encoding="utf-8") as stream:
                expectation = json.load(stream)["expect"]
            assert expectation.get("error") == identity, case

    def test_the_name_key_accepts_what_the_loader_accepts(self):
        document = {"name": "vendor"}
        assert not list(self._validator().iter_errors(document))

    @pytest.mark.parametrize(
        "document",
        [
            {"name": "@vendor"},
            {"name": "a/b"},
            {"name": ""},
            {"name": ["vendor"]},
        ],
    )
    def test_the_new_keys_reject_what_the_loader_rejects(self, document):
        assert list(self._validator().iter_errors(document))

    def test_name_characters_accepted_by_the_loader_are_accepted_by_the_schema(self):
        document = {
            "name": "vendor[1]{stable}",
            "files": ["notes[1].inc", "gates{v2}.inc"],
            "programs": ["notes[1].inc"],
            "libraries": {"gates{v2}": {"path": "../vendor"}},
        }

        assert not list(self._validator().iter_errors(document))

    @pytest.mark.parametrize(
        "document",
        [
            {"name": "vendor*"},
            {"name": "vendor?"},
            {"files": ["gates*.inc"]},
            {"files": ["gates?.inc"]},
            {"libraries": {"vendor*": {"path": "../vendor"}}},
            {"libraries": {"vendor?": {"path": "../vendor"}}},
        ],
    )
    def test_glob_characters_rejected_by_the_loader_are_rejected_by_the_schema(self, document):
        assert list(self._validator().iter_errors(document))

    @pytest.mark.parametrize("form", ["NFC", "NFD"])
    def test_normalization_forms_are_accepted_individually_without_rewriting(self, form):
        name = unicodedata.normalize(form, "caf\u00e9")
        document = {"name": name, "files": [name + ".inc"]}

        assert not list(self._validator().iter_errors(document))

    def test_normalization_pair_collisions_are_left_to_the_loader(self):
        composed = unicodedata.normalize("NFC", "caf\u00e9")
        decomposed = unicodedata.normalize("NFD", composed)
        documents = [
            {"files": [composed + ".inc", decomposed + ".inc"]},
            {
                "libraries": {
                    composed: {"path": "../one"},
                    decomposed: {"path": "../two"},
                }
            },
        ]

        assert all(not list(self._validator().iter_errors(item)) for item in documents)

    def test_the_name_key_keeps_its_description_despite_the_reference(self):
        # Draft 7 ignores keywords beside a $ref, so an annotated reference is
        # written as a single-element allOf.  A plain $ref here would silently
        # drop the description an editor shows.
        with open(SCHEMA_PATH, encoding="utf-8") as stream:
            schema = json.load(stream)
        name = schema["properties"]["name"]
        assert "$ref" not in name
        assert name["description"]


class TestLoadedProjectState:
    def test_sources_and_library_bindings_are_immutable_snapshots(self):
        sources = {
            "main.qasm": 'OPENQASM 3.0;\ninclude "@v/gates.inc";',
            "@vendor/gates.inc": "gate g q { U(0, 0, 0) q; }",
            "@other/gates.inc": "gate other q { U(0, 0, 0) q; }",
        }
        root_bindings = {"v": "vendor"}
        library_bindings = {"": root_bindings, "vendor": {}}
        loaded = LoadedProject(sources=sources, library_bindings=library_bindings)

        sources["@vendor/gates.inc"] = "changed"
        root_bindings["v"] = "other"
        library_bindings["new"] = {"v": "other"}

        assert loaded.sources["@vendor/gates.inc"] == "gate g q { U(0, 0, 0) q; }"
        assert loaded.library_bindings == {"": {"v": "vendor"}, "vendor": {}}
        assert loaded.environment.resolve("@v/gates.inc", "main.qasm").canonical_name == (
            "@vendor/gates.inc"
        )
        with pytest.raises(TypeError):
            loaded.sources["main.qasm"] = "changed"  # type: ignore[index]
        with pytest.raises(TypeError):
            loaded.library_bindings[""] = {}  # type: ignore[index]
        with pytest.raises(TypeError):
            loaded.library_bindings[""]["v"] = "other"  # type: ignore[index]

    def test_fields_are_frozen_and_environment_is_not_a_constructor_input(self):
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"})

        with pytest.raises(FrozenInstanceError):
            setattr(loaded, "compilation_root", "main.qasm")
        with pytest.raises(TypeError, match="environment"):
            # pylint: disable-next=unexpected-keyword-arg
            LoadedProject(sources={}, environment=None)  # type: ignore[call-arg]

    def test_empty_scoped_bindings_fail_closed(self):
        loaded = LoadedProject(
            sources={
                "main.qasm": 'OPENQASM 3.0;\ninclude "@vendor/gates.inc";',
                "@vendor/gates.inc": "gate g q { U(0, 0, 0) q; }",
            },
            library_bindings={"": {}, "vendor": {}},
        )

        with pytest.raises(IncludeNotFoundError):
            loaded.environment.resolve("@vendor/gates.inc", "main.qasm")


class TestOptInImport:
    def test_project_import_does_not_require_a_subscriptable_pathlike(self):
        script = (
            "import os, openqasm3\n"
            "class PathLike:\n"
            "    pass\n"
            "os.PathLike = PathLike\n"
            "import openqasm3.project\n"
        )

        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, check=False
        )

        assert result.returncode == 0, result.stderr

    def test_importing_the_package_does_not_import_this_module(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys, openqasm3; "
                "sys.exit(1 if 'openqasm3.project' in sys.modules else 0)",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "openqasm3.project must not be imported eagerly"

    def test_importing_the_parser_does_not_import_the_project_module(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys, openqasm3.parser; "
                "sys.exit(1 if 'openqasm3.project' in sys.modules else 0)",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, "openqasm3.parser must consume projects structurally"

    def test_module_needs_no_parser(self):
        import openqasm3.project as module

        source = open(module.__file__, encoding="utf-8").read()
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert "antlr4" not in stripped
                assert "openqasm3.parser" not in stripped

    def test_a_project_loads_with_the_parser_unavailable(self, tmp_path):
        # The textual check above cannot see a transitive import, and merely observing that
        # antlr4 is absent from sys.modules proves nothing on a machine where it is installed.
        # Deny the import outright: an environment without the [parser] extra must still be
        # able to produce sources for a compiler that has its own front end.
        write(tmp_path, "main.qasm", "OPENQASM 3.0;\n")
        script = (
            "import sys, json\n"
            "class Block:\n"
            "    def find_spec(self, name, path=None, target=None):\n"
            "        if name == 'antlr4' or name.startswith('antlr4.'):\n"
            "            raise ModuleNotFoundError('antlr4 is unavailable')\n"
            "        return None\n"
            "sys.meta_path.insert(0, Block())\n"
            "from openqasm3.project import load_project\n"
            "print(json.dumps(sorted(load_project(sys.argv[1]).sources)))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout) == ["main.qasm"]


class TestLibraries:
    """A library is a project loaded from outside the root that references it."""

    GATE = "gate g q { U(0, 0, 0) q; }\n"

    def library(self, root, name, files=None, **libraries):
        """Create a library, which declares the name its canonical names are formed from."""
        manifest = {"name": name}
        if libraries:
            manifest["libraries"] = {n: {"path": path} for n, path in libraries.items()}
        return project(root, json.dumps(manifest), files or {"x.inc": self.GATE})

    def declare(self, tmp_path, **libraries):
        spec = {name: {"path": path} for name, path in libraries.items()}
        return project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": spec}),
            files={"main.qasm": 'OPENQASM 3.0;\ninclude "@vendor/gates.inc";\n'},
        )

    @pytest.mark.parametrize(
        ("field", "value", "identity"),
        [
            ("files", "gates.inc", "files-declaration-invalid"),
            ("programs", "gates.inc", "programs-declaration-invalid"),
            ("libraries", [], "library-declaration-invalid"),
        ],
    )
    def test_library_manifest_recognized_fields_are_semantically_validated(
        self, tmp_path, field, value, identity
    ):
        manifest = {"name": "vendor", field: value}
        project(tmp_path / "vendor", json.dumps(manifest), {"gates.inc": self.GATE})

        with pytest.raises(ProjectError) as caught:
            load_project(self.declare(tmp_path, vendor="../vendor"))

        assert caught.value.identity == identity

    def test_declared_library_is_loaded_under_the_name_it_declares(self, tmp_path):
        self.library(tmp_path / "vendor", "vendor", files={"gates.inc": self.GATE})
        loaded = load_project(self.declare(tmp_path, vendor="../vendor"))
        assert sorted(loaded.sources) == ["@vendor/gates.inc", "main.qasm"]
        assert loaded.library_bindings == {"": {"vendor": "vendor"}, "vendor": {}}

    def test_an_apparent_name_may_differ_from_the_declared_name(self, tmp_path):
        self.library(tmp_path / "vendor", "acme", files={"gates.inc": self.GATE})
        loaded = load_project(self.declare(tmp_path, v="../vendor"))
        assert sorted(loaded.sources) == ["@acme/gates.inc", "main.qasm"]
        assert loaded.library_bindings[""] == {"v": "acme"}

    def test_brackets_and_braces_are_usable_in_library_names(self, tmp_path):
        canonical = "vendor[1]{stable}"
        apparent = "v[1]{stable}"
        self.library(tmp_path / "vendor", canonical, files={"gates{v2}.inc": self.GATE})
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {apparent: {"path": "../vendor"}}}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )

        loaded = load_project(root)

        assert sorted(loaded.sources) == [f"@{canonical}/gates{{v2}}.inc", "main.qasm"]
        assert loaded.library_bindings[""] == {apparent: canonical}

    @pytest.mark.parametrize("form", ["NFC", "NFD"])
    def test_library_name_spelling_is_preserved(self, tmp_path, form):
        name = unicodedata.normalize(form, "caf\u00e9")
        self.library(tmp_path / "vendor", name)

        loaded = load_project(self.declare(tmp_path, vendor="../vendor"))

        assert f"@{name}/x.inc" in loaded.sources
        assert loaded.library_bindings[""] == {"vendor": name}

    def test_apparent_library_names_differing_only_by_normalization_collide(self, tmp_path):
        composed = unicodedata.normalize("NFC", "caf\u00e9")
        decomposed = unicodedata.normalize("NFD", composed)
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {
                    "libraries": {
                        composed: {"path": "../absent-one"},
                        decomposed: {"path": "../absent-two"},
                    }
                }
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )

        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)

        assert caught.value.identity == "canonical-name-normalization-collision"

    def test_apparent_library_normalization_scope_is_local_to_each_project(self, tmp_path):
        composed = unicodedata.normalize("NFC", "caf\u00e9")
        decomposed = unicodedata.normalize("NFD", composed)
        self.library(tmp_path / "red", "red")
        self.library(tmp_path / "blue", "blue")
        self.library(tmp_path / "liba", "liba", {"a.inc": self.GATE}, **{composed: "../red"})
        self.library(tmp_path / "libb", "libb", {"b.inc": self.GATE}, **{decomposed: "../blue"})
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../liba"}, "b": {"path": "../libb"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )

        loaded = load_project(root)

        assert loaded.library_bindings["liba"] == {composed: "red"}
        assert loaded.library_bindings["libb"] == {decomposed: "blue"}

    def test_canonical_library_names_differing_only_by_normalization_collide(self, tmp_path):
        composed = unicodedata.normalize("NFC", "caf\u00e9")
        decomposed = unicodedata.normalize("NFD", composed)
        project(tmp_path / "one", json.dumps({"name": composed}), files={})
        project(tmp_path / "two", json.dumps({"name": decomposed}), files={})
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"one": {"path": "../one"}, "two": {"path": "../two"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )

        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)

        assert caught.value.identity == "canonical-name-normalization-collision"

    def test_canonical_library_normalization_scope_spans_transitive_branches(self, tmp_path):
        composed = unicodedata.normalize("NFC", "caf\u00e9")
        decomposed = unicodedata.normalize("NFD", composed)
        project(tmp_path / "one", json.dumps({"name": composed}), files={})
        project(tmp_path / "two", json.dumps({"name": decomposed}), files={})
        self.library(tmp_path / "liba", "liba", {"a.inc": self.GATE}, deep="../one")
        self.library(tmp_path / "libb", "libb", {"b.inc": self.GATE}, deep="../two")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../liba"}, "b": {"path": "../libb"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )

        with pytest.raises(CanonicalNameError) as caught:
            load_project(root)

        assert caught.value.identity == "canonical-name-normalization-collision"

    def test_library_without_a_manifest_is_refused(self, tmp_path):
        """A directory that declares no name is not a library; the consumer cannot name it."""
        write(tmp_path / "vendor", "gates.inc", self.GATE)
        with pytest.raises(LibraryError) as caught:
            load_project(self.declare(tmp_path, vendor="../vendor"))
        assert caught.value.identity == "library-name-undeclared"

    def test_library_without_a_declared_name_is_refused(self, tmp_path):
        project(tmp_path / "vendor", files={"gates.inc": self.GATE})
        with pytest.raises(LibraryError) as caught:
            load_project(self.declare(tmp_path, vendor="../vendor"))
        assert caught.value.identity == "library-name-undeclared"

    @pytest.mark.parametrize("declared", ["a/b", "@a", "", ".", "..", "a*", "a?", 42])
    def test_an_unusable_declared_name_is_refused(self, tmp_path, declared):
        project(tmp_path / "vendor", json.dumps({"name": declared}), {"gates.inc": self.GATE})
        with pytest.raises(LibraryError) as caught:
            load_project(self.declare(tmp_path, vendor="../vendor"))
        assert caught.value.identity == "library-declaration-invalid"

    def test_library_of_a_library_is_loaded_transitively(self, tmp_path):
        self.library(tmp_path / "deep", "deep", files={"base.inc": self.GATE})
        self.library(tmp_path / "vendor", "vendor", {"gates.inc": self.GATE}, deep="../deep")
        loaded = load_project(self.declare(tmp_path, vendor="../vendor"))
        assert sorted(loaded.sources) == ["@deep/base.inc", "@vendor/gates.inc", "main.qasm"]
        assert loaded.library_bindings == {
            "": {"vendor": "vendor"},
            "vendor": {"deep": "deep"},
            "deep": {},
        }

    def test_a_library_of_a_library_is_absent_from_the_root_map(self, tmp_path):
        """Visibility is not transitive, even though the source text is loaded once."""
        self.library(tmp_path / "deep", "deep", files={"base.inc": self.GATE})
        self.library(tmp_path / "vendor", "vendor", {"gates.inc": self.GATE}, deep="../deep")
        loaded = load_project(self.declare(tmp_path, vendor="../vendor"))
        assert "@deep/base.inc" in loaded.sources
        assert "deep" not in loaded.library_bindings[""]

    def test_one_library_reached_twice_is_loaded_once(self, tmp_path):
        self.library(tmp_path / "shared", "shared", files={"s.inc": self.GATE})
        self.library(tmp_path / "vendor", "vendor", {"gates.inc": self.GATE}, shared="../shared")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"vendor": {"path": "../vendor"}, "shared": {"path": "../shared"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        assert sorted(load_project(root).sources) == [
            "@shared/s.inc",
            "@vendor/gates.inc",
            "main.qasm",
        ]

    def test_one_library_under_two_apparent_names_is_loaded_once(self, tmp_path):
        """One root, two names: a shape the flat namespace could only diagnose."""
        self.library(tmp_path / "vendor", "vendor", files={"gates.inc": self.GATE})
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"v": {"path": "../vendor"}, "w": {"path": "../vendor"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        loaded = load_project(root)
        assert sorted(loaded.sources) == ["@vendor/gates.inc", "main.qasm"]
        assert loaded.library_bindings[""] == {"v": "vendor", "w": "vendor"}

    def test_two_projects_may_use_one_apparent_name_for_different_libraries(self, tmp_path):
        """Two roots, one name: the other shape the flat namespace could only diagnose."""
        self.library(tmp_path / "red", "red", files={"g.inc": self.GATE})
        self.library(tmp_path / "blue", "blue", files={"g.inc": self.GATE})
        self.library(tmp_path / "liba", "liba", {"a.inc": self.GATE}, c="../red")
        self.library(tmp_path / "libb", "libb", {"b.inc": self.GATE}, c="../blue")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../liba"}, "b": {"path": "../libb"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        loaded = load_project(root)
        assert sorted(loaded.sources) == [
            "@blue/g.inc",
            "@liba/a.inc",
            "@libb/b.inc",
            "@red/g.inc",
            "main.qasm",
        ]
        assert loaded.library_bindings["liba"] == {"c": "red"}
        assert loaded.library_bindings["libb"] == {"c": "blue"}

    def test_two_roots_declaring_one_name_are_refused(self, tmp_path):
        """Names remain conventionally unique; a genuine collision is still diagnosed."""
        self.library(tmp_path / "one", "collide", files={"x.inc": self.GATE})
        self.library(tmp_path / "two", "collide", files={"y.inc": self.GATE})
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"a": {"path": "../one"}, "b": {"path": "../two"}}}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-binding-conflict"

    def test_a_root_nested_inside_a_bound_root_is_refused(self, tmp_path):
        """Reproduced: one file was reachable as both '@inner/i.inc' and '@outer/inner/i.inc'."""
        self.library(tmp_path / "outer", "outer", files={"o.inc": self.GATE})
        self.library(tmp_path / "outer" / "inner", "inner", files={"i.inc": self.GATE})
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"o": {"path": "../outer"}, "i": {"path": "../outer/inner"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-root-overlap"

    def test_a_root_containing_a_bound_root_is_refused(self, tmp_path):
        """Containment is refused in both directions, so declaration order cannot matter."""
        self.library(tmp_path / "outer", "outer", files={"o.inc": self.GATE})
        self.library(tmp_path / "outer" / "inner", "inner", files={"i.inc": self.GATE})
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {
                    "libraries": {
                        "a_inner": {"path": "../outer/inner"},
                        "z_outer": {"path": "../outer"},
                    }
                }
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-root-overlap"

    def test_a_root_nested_inside_a_bound_root_is_refused_transitively(self, tmp_path):
        """The overlap is with a root bound earlier, not with the project that declares it."""
        self.library(tmp_path / "outer" / "inner", "inner", files={"i.inc": self.GATE})
        self.library(tmp_path / "outer", "outer", {"o.inc": self.GATE}, i="inner")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"o": {"path": "../outer"}}}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-root-overlap"

    def test_sibling_roots_in_one_tree_still_load(self, tmp_path):
        """A monorepo of sibling projects is not an overlap and must keep working."""
        self.library(tmp_path / "mono" / "liba", "liba", files={"a.inc": self.GATE})
        self.library(tmp_path / "mono" / "libb", "libb", files={"b.inc": self.GATE})
        root = project(
            tmp_path / "mono" / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../liba"}, "b": {"path": "../libb"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        assert sorted(load_project(root).sources) == ["@liba/a.inc", "@libb/b.inc", "main.qasm"]

    def test_one_library_root_reached_by_two_paths_binds_once(self, tmp_path):
        """Two declared paths naming one directory are one library, not two."""
        self.library(tmp_path / "vendor", "vendor", files={"gates.inc": self.GATE})
        try:
            os.symlink(str(tmp_path / "vendor"), str(tmp_path / "alias"), target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError):
            pytest.skip("this host cannot create a symbolic link")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../vendor"}, "b": {"path": "../alias"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        loaded = load_project(root)
        assert sorted(loaded.sources) == ["@vendor/gates.inc", "main.qasm"]
        # Both apparent names reach the one library, which is loaded once.
        assert loaded.library_bindings[""] == {"a": "vendor", "b": "vendor"}

    def test_case_differing_paths_to_one_library_bind_once(self, tmp_path):
        self.library(tmp_path / "vendor", "vendor", files={"gates.inc": self.GATE})
        if not os.path.isdir(str(tmp_path / "VENDOR")):
            pytest.skip("this volume distinguishes case, so '../VENDOR' names nothing")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"a": {"path": "../vendor"}, "b": {"path": "../VENDOR"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        loaded = load_project(root)
        assert sorted(loaded.sources) == ["@vendor/gates.inc", "main.qasm"]

    def test_library_inside_the_referencing_root_is_refused(self, tmp_path):
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"v": {"path": "inner"}}}),
            files={"inner/g.inc": self.GATE},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-root-overlap"

    def test_missing_library_is_diagnosed(self, tmp_path):
        root = self.declare(tmp_path, vendor="../absent")
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-missing"

    def test_a_cycle_back_to_a_loading_project_is_refused(self, tmp_path):
        self.library(tmp_path / "a", "a", {"x.inc": self.GATE}, r="../app")
        root = self.declare(tmp_path, v="../a")
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-cycle"

    @pytest.mark.parametrize("back_name", ["a", "alternate"])
    def test_a_deep_cycle_back_to_an_active_library_is_refused(self, tmp_path, back_name):
        self.library(tmp_path / "b", "b", {"b.inc": self.GATE}, **{back_name: "../a"})
        self.library(tmp_path / "a", "a", {"a.inc": self.GATE}, b="../b")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"a": {"path": "../a"}}}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-cycle"

    @pytest.mark.parametrize(
        "spec",
        [
            '"../a"',
            '{"git": "https://example.invalid/a"}',
            '{"path": "/tmp"}',
            '{"path": "..\\\\a"}',
            '{"path": ""}',
            "42",
        ],
        ids=["bare-string", "no-path", "absolute", "backslash", "empty", "not-object"],
    )
    def test_malformed_declaration_is_refused(self, tmp_path, spec):
        self.library(tmp_path / "a", "a")
        root = project(
            tmp_path / "app",
            manifest='{"libraries": {"v": %s}}' % spec,
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-declaration-invalid"

    @pytest.mark.parametrize("name", ["a/b", "@a", "", ".", "..", "a*", "a?"])
    def test_an_unusable_apparent_name_is_refused(self, tmp_path, name):
        self.library(tmp_path / "a", "a")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {name: {"path": "../a"}}}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(LibraryError) as caught:
            load_project(root)
        assert caught.value.identity == "library-declaration-invalid"

    def test_an_unrecognized_key_in_a_declaration_is_ignored(self, tmp_path):
        self.library(tmp_path / "a", "a")
        root = project(
            tmp_path / "app",
            manifest=json.dumps(
                {"libraries": {"v": {"path": "../a", "version": "1.0", "git": "u"}}}
            ),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        assert "@a/x.inc" in load_project(root).sources

    def test_declared_programs_name_only_this_project_s_files(self, tmp_path):
        self.library(tmp_path / "a", "a")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"v": {"path": "../a"}}, "programs": ["main.qasm"]}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        assert load_project(root).programs == ("main.qasm",)

    def test_a_library_file_may_not_be_declared_a_program(self, tmp_path):
        self.library(tmp_path / "a", "a")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"v": {"path": "../a"}}, "programs": ["@a/x.inc"]}),
            files={"main.qasm": "OPENQASM 3.0;"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "files-name-invalid"

    def test_library_source_units_resolve_through_the_parser(self, tmp_path):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        pytest.importorskip("antlr4", reason="needs the [parser] extra")
        self.library(tmp_path / "deep", "deep", files={"base.inc": self.GATE})
        self.library(
            tmp_path / "vendor",
            "vendor",
            {"gates.inc": 'include "@d/base.inc";\n' + self.GATE},
            d="../deep",
        )
        loaded = load_project(self.declare(tmp_path, vendor="../vendor"))
        program = openqasm3.parse_project(loaded, "main.qasm")
        # The library writes '@d/', which its own map translates to the declared '@deep/'.
        assert [unit.canonical_name for unit in program.sources] == [
            "main.qasm",
            "@vendor/gates.inc",
            "@deep/base.inc",
        ]

    def test_a_project_cannot_reach_a_library_it_did_not_declare(self, tmp_path):
        """The reproduced leak, exercised through the documented load-then-parse path."""
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        pytest.importorskip("antlr4", reason="needs the [parser] extra")
        from openqasm3.resolver import IncludeNotFoundError

        self.library(tmp_path / "deep", "deep", files={"base.inc": self.GATE})
        self.library(tmp_path / "vendor", "vendor", {"gates.inc": self.GATE}, d="../deep")
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"vendor": {"path": "../vendor"}}}),
            files={"main.qasm": 'OPENQASM 3.0;\ninclude "@deep/base.inc";\n'},
        )
        loaded = load_project(root)
        assert "@deep/base.inc" in loaded.sources
        with pytest.raises(IncludeNotFoundError):
            openqasm3.parse_project(loaded, "main.qasm")

    def test_a_library_resolves_its_own_names_within_itself(self, tmp_path):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        pytest.importorskip("antlr4", reason="needs the [parser] extra")
        self.library(
            tmp_path / "vendor",
            "vendor",
            {"gates.inc": 'include "helper.inc";\n', "helper.inc": self.GATE},
        )
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"vendor": {"path": "../vendor"}}}),
            files={
                "main.qasm": 'OPENQASM 3.0;\ninclude "@vendor/gates.inc";\n',
                "helper.inc": "gate shadow q { U(0, 0, 0) q; }\n",
            },
        )
        loaded = load_project(root)
        program = openqasm3.parse_project(loaded, "main.qasm")
        # The library reaches its own helper, not the same-named file in the using project.
        assert [unit.canonical_name for unit in program.sources] == [
            "main.qasm",
            "@vendor/gates.inc",
            "@vendor/helper.inc",
        ]


class TestParseProject:
    def test_compilation_root_is_used_when_name_is_omitted(self):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"}, compilation_root="main.qasm")

        program = openqasm3.parse_project(loaded)

        assert program.sources[0].canonical_name == "main.qasm"

    def test_explicit_name_overrides_the_compilation_root(self):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        loaded = LoadedProject(
            sources={
                "main.qasm": "OPENQASM 3.0;",
                "other.qasm": "OPENQASM 3.0;",
            },
            compilation_root="main.qasm",
        )

        program = openqasm3.parse_project(loaded, "other.qasm")

        assert program.sources[0].canonical_name == "other.qasm"

    def test_missing_selection_is_rejected(self):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"})

        with pytest.raises(
            ValueError, match="'name' is required when the project has no compilation root"
        ):
            openqasm3.parse_project(loaded)

    def test_parser_options_are_forwarded(self, monkeypatch):
        parser = pytest.importorskip("openqasm3.parser", reason="needs the [parser] extra")
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"})
        expected = object()
        received = {}

        def fake_parse(input_, **kwargs):
            received["input"] = input_
            received.update(kwargs)
            return expected

        monkeypatch.setattr(parser, "parse", fake_parse)

        actual = parser.parse_project(loaded, "main.qasm", permissive=True, ignore_version=True)

        assert actual is expected
        assert received == {
            "input": "OPENQASM 3.0;",
            "permissive": True,
            "ignore_version": True,
            "includes": loaded.environment,
            "name": "main.qasm",
        }

    def test_public_signatures_take_one_project(self):
        import inspect

        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")

        parse_parameters = inspect.signature(openqasm3.parse_project).parameters
        derive_parameters = inspect.signature(openqasm3.derive_programs).parameters

        assert tuple(parse_parameters) == (
            "project",
            "name",
            "permissive",
            "ignore_version",
        )
        assert parse_parameters["permissive"].kind is inspect.Parameter.KEYWORD_ONLY
        assert parse_parameters["ignore_version"].kind is inspect.Parameter.KEYWORD_ONLY
        assert tuple(derive_parameters) == ("project",)

    def test_unknown_selection_is_rejected_before_parsing(self):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"})

        with pytest.raises(ValueError, match="source 'absent.qasm' is not present"):
            openqasm3.parse_project(loaded, "absent.qasm")

    @pytest.mark.parametrize(
        ("name", "error", "message"),
        [
            ("", ValueError, "a source identity must not be empty"),
            (42, TypeError, "a source identity must be a string, not int"),
        ],
    )
    def test_explicit_name_is_validated(self, name, error, message):
        openqasm3 = pytest.importorskip("openqasm3", reason="needs the [parser] extra")
        loaded = LoadedProject(sources={"main.qasm": "OPENQASM 3.0;"})

        with pytest.raises(error, match=message):
            openqasm3.parse_project(loaded, name)


class TestDerivedPrograms:
    """The include-graph derivation a host performs when the manifest declares no programs."""

    GATE = "gate g q { U(0, 0, 0) q; }\n"

    def derive(self, root):
        parser = pytest.importorskip("openqasm3.parser", reason="needs the [parser] extra")
        loaded = load_project(root)
        return loaded, parser.derive_programs(loaded)

    def test_a_source_unit_another_includes_is_not_a_program(self, tmp_path):
        root = project(
            tmp_path,
            files={
                "main.qasm": 'OPENQASM 3.0;\ninclude "lib/helper.inc";\n',
                "lib/helper.inc": self.GATE,
                "other.qasm": "OPENQASM 3.0;\n",
            },
        )
        _, derived = self.derive(root)
        assert derived == ("main.qasm", "other.qasm")

    def test_targets_are_resolved_rather_than_matched_as_text(self, tmp_path):
        """A '//' target names no file called '//top.inc', so text matching derives no edge."""
        root = project(
            tmp_path,
            files={"lib/a.qasm": 'OPENQASM 3.0;\ninclude "//top.inc";\n', "top.inc": self.GATE},
        )
        _, derived = self.derive(root)
        assert derived == ("lib/a.qasm",)

    def test_the_reserved_name_is_not_an_inclusion(self, tmp_path):
        root = project(
            tmp_path,
            files={
                "main.qasm": 'OPENQASM 3.0;\ninclude "stdgates.inc";\n',
                "b.qasm": "OPENQASM 3.0;\n",
            },
        )
        _, derived = self.derive(root)
        assert derived == ("b.qasm", "main.qasm") or derived == ("main.qasm", "b.qasm")

    def test_library_files_are_neither_programs_nor_includers(self, tmp_path):
        project(
            tmp_path / "vendor",
            manifest=json.dumps({"name": "vendor"}),
            files={"gates.inc": 'include "helper.inc";\n', "helper.inc": self.GATE},
        )
        root = project(
            tmp_path / "app",
            manifest=json.dumps({"libraries": {"v": {"path": "../vendor"}}}),
            files={"main.qasm": 'OPENQASM 3.0;\ninclude "@v/gates.inc";\n'},
        )
        loaded, derived = self.derive(root)
        assert "@vendor/gates.inc" in loaded.sources
        assert derived == ("main.qasm",)

    def test_a_full_cycle_derives_every_source_unit(self, tmp_path):
        root = project(
            tmp_path,
            files={"a.inc": 'include "b.inc";\n', "b.inc": 'include "a.inc";\n'},
        )
        _, derived = self.derive(root)
        assert sorted(derived) == ["a.inc", "b.inc"]

    def test_every_present_candidate_contributes_an_edge(self):
        parser = pytest.importorskip("openqasm3.parser", reason="needs the [parser] extra")

        class Environment:
            def candidates(self, target, includer):
                assert (target, includer) == ("target.inc", "main.qasm")
                return ("first.inc", "second.inc")

            def resolve(self, target, includer):
                raise AssertionError("derivation must not resolve an ambiguous target")

        class Project:
            sources = {
                "main.qasm": 'include "target.inc";',
                "first.inc": self.GATE,
                "second.inc": self.GATE,
            }
            environment = Environment()
            compilation_root = None

        assert parser.derive_programs(Project()) == ("main.qasm",)

    def test_a_library_with_no_internal_inclusions_derives_everything(self, tmp_path):
        """The heuristic's documented failure: 'programs': [] is how an author says otherwise."""
        root = project(tmp_path, files={"a.inc": self.GATE, "b.inc": self.GATE})
        _, derived = self.derive(root)
        assert sorted(derived) == ["a.inc", "b.inc"]

    def test_the_declaration_is_untouched_by_the_derivation(self, tmp_path):
        """`programs` keeps meaning what the manifest said, including when it said nothing."""
        root = project(
            tmp_path,
            files={"main.qasm": 'OPENQASM 3.0;\ninclude "helper.inc";\n', "helper.inc": self.GATE},
        )
        loaded, derived = self.derive(root)
        assert loaded.programs is None
        assert derived == ("main.qasm",)

        declared = project(
            tmp_path / "declared",
            manifest=json.dumps({"programs": ["helper.inc"]}),
            files={"main.qasm": 'OPENQASM 3.0;\ninclude "helper.inc";\n', "helper.inc": self.GATE},
        )
        assert load_project(declared).programs == ("helper.inc",)

    def test_a_project_holding_an_unparseable_file_still_loads(self, tmp_path):
        """Loading never parses, so one broken file does not cost a language service the rest."""
        root = project(
            tmp_path,
            files={"main.qasm": "OPENQASM 3.0;\n", "broken.qasm": "this is not OpenQASM {{{\n"},
        )
        assert set(load_project(root).sources) == {"main.qasm", "broken.qasm"}

    def test_the_derivation_reports_a_source_unit_it_cannot_parse(self, tmp_path):
        parser = pytest.importorskip("openqasm3.parser", reason="needs the [parser] extra")
        root = project(
            tmp_path,
            files={"main.qasm": "OPENQASM 3.0;\n", "broken.qasm": "this is not OpenQASM {{{\n"},
        )
        loaded = load_project(root)
        with pytest.raises(parser.QASM3ParsingError):
            parser.derive_programs(loaded)


class TestReservedLibraryPrefix:
    def test_a_declared_file_may_not_begin_a_component_with_the_prefix(self, tmp_path):
        root = project(
            tmp_path,
            manifest='{"files": ["@v/x.inc"]}',
            files={"@v/x.inc": "gate g q { U(0, 0, 0) q; }\n"},
        )
        with pytest.raises(FileSetError) as caught:
            load_project(root)
        assert caught.value.identity == "files-name-invalid"

    def test_the_default_walk_skips_a_prefixed_entry(self, tmp_path):
        root = project(
            tmp_path,
            files={
                "@v/x.inc": "gate g q { U(0, 0, 0) q; }\n",
                "ok.inc": "gate k q { U(0, 0, 0) q; }\n",
            },
        )
        assert sorted(load_project(root).sources) == ["ok.inc"]
