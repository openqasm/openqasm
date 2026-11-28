"""Literal process-contract tests for the project conformance harness."""

import importlib.util
import os

import pytest


CORPUS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "conformance", "project")
)


def _load_harness():
    spec = importlib.util.spec_from_file_location(
        "openqasm_conformance_protocol_harness", os.path.join(CORPUS, "harness.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "openqasm_reference_protocol_runner",
        os.path.join(CORPUS, "runners", "python", "runner.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HARNESS = _load_harness()
RUNNER = _load_runner()


@pytest.mark.parametrize(
    ("entry_key", "entry_value"),
    [
        ("project_root", "project"),
        ("manifest_path", "project/openqasm.json"),
        ("discover_from", "project"),
    ],
)
def test_entry_modes_exempt_only_the_selected_reserved_root(tmp_path, entry_key, entry_value):
    project = tmp_path / "project"
    project.mkdir()
    (project / "openqasm.json").write_text('{"files": ["stdgates.inc"]}', encoding="utf-8")
    (project / "stdgates.inc").write_text("OPENQASM 3.0;\n", encoding="utf-8")
    request = {"case_dir": str(tmp_path), "class": "loader", entry_key: entry_value}

    unselected = RUNNER.run(request)
    request["subject"] = "stdgates.inc"
    selected = RUNNER.run(request)

    assert unselected == {"error": "canonical-name-reserved"}
    assert selected == {
        "canonical_names": ["stdgates.inc"],
        "root_canonical_name": "stdgates.inc",
        "programs": None,
    }


@pytest.mark.parametrize(
    "result",
    [
        {"error": "manifest-json-invalid"},
        {"sources": ["main.qasm"]},
        {"canonical_names": [], "programs": None},
        {
            "canonical_names": ["main.qasm"],
            "root_canonical_name": "main.qasm",
            "programs": [],
        },
        {"derived_programs": ["z-main.qasm", "a-independent.qasm"]},
        {"skipped": "parser class not implemented"},
    ],
)
def test_result_contract_accepts_exact_variants(result):
    assert HARNESS._result_shape_disagreement(result) is None


@pytest.mark.parametrize(
    "result",
    [
        {"error": "manifest-json-invalid", "sources": []},
        {"error": "manifest-json-invalid", "details": "diagnostic"},
        {"sources": [], "programs": None},
        {"canonical_names": []},
        {"programs": None},
        {"skipped": "not implemented", "error": "manifest-json-invalid"},
        {"error": 1},
        {"sources": [1]},
        {"canonical_names": [1], "programs": None},
        {"canonical_names": [], "programs": [1]},
        {"canonical_names": [], "root_canonical_name": 1, "programs": None},
        {"derived_programs": [1]},
        {"skipped": False},
    ],
)
def test_result_contract_rejects_non_union_shapes(result):
    assert HARNESS._result_shape_disagreement(result) is not None


@pytest.mark.parametrize(
    "expect",
    [
        {"error": "manifest-json-invalid"},
        {"sources": ["main.qasm"]},
        {"canonical_names": [], "programs": None},
        {
            "canonical_names": ["main.qasm"],
            "root_canonical_name": "main.qasm",
            "programs": [],
        },
        {"derived_programs": ["z-main.qasm", "a-independent.qasm"]},
    ],
)
def test_expectation_contract_accepts_exact_comparable_variants(expect):
    assert HARNESS._expectation_shape_disagreement(expect) is None


@pytest.mark.parametrize(
    "expect",
    [
        {"canonical_names": []},
        {"error": "manifest-json-invalid", "sources": []},
        {"sources": [], "details": "diagnostic"},
        {"skipped": "parser class not implemented"},
        {"error": 1},
        {"sources": [1]},
        {"canonical_names": [], "programs": [1]},
        {"derived_programs": [1]},
    ],
)
def test_expectation_contract_rejects_partial_and_noncomparable_variants(expect):
    assert HARNESS._expectation_shape_disagreement(expect) is not None


def test_compare_rejects_illegal_fields_before_matching_values():
    result = {"error": "manifest-json-invalid", "sources": []}

    disagreement = HARNESS._compare({"error": "manifest-json-invalid"}, result)

    assert disagreement == "result must contain exactly one discriminator, got %r" % result


@pytest.mark.parametrize(
    ("identity", "expected"),
    [
        ("files-missing", "files-missing"),
        ("manifest-unreadable", None),
        (None, None),
        (["files-missing"], None),
    ],
)
def test_runner_reports_only_portable_error_identities(identity, expected):
    error = RuntimeError("failure")
    error.identity = identity

    assert RUNNER._identity_of(error) == expected


def test_loader_subject_must_name_a_project_source(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "openqasm.json").write_text("{}", encoding="utf-8")
    (project / "main.qasm").write_text("OPENQASM 3.0;\n", encoding="utf-8")

    with pytest.raises(RUNNER.RunnerFailure, match="absent.qasm"):
        RUNNER.run(
            {
                "case_dir": str(tmp_path),
                "class": "loader",
                "project_root": "project",
                "subject": "absent.qasm",
            }
        )


def test_run_case_rejects_contradictory_skip_before_classifying_it(monkeypatch, tmp_path):
    monkeypatch.setattr(
        HARNESS,
        "_read_case",
        lambda _case_dir: {"class": "loader", "expect": {"error": "project-error"}},
    )
    monkeypatch.setattr(
        HARNESS,
        "_invoke",
        lambda _command, _request: {
            "skipped": "not implemented",
            "error": "project-error",
        },
    )

    outcome = HARNESS.run_case([], "literal-protocol", str(tmp_path))

    assert outcome["outcome"] == HARNESS.FAIL
    assert "exactly one discriminator" in outcome["reason"]


def test_run_case_rejects_an_incomplete_expectation_before_invoking_runner(monkeypatch, tmp_path):
    monkeypatch.setattr(
        HARNESS,
        "_read_case",
        lambda _case_dir: {"class": "loader", "expect": {"canonical_names": []}},
    )

    def fail_if_invoked(_command, _request):
        raise AssertionError("runner should not be invoked for an invalid expectation")

    monkeypatch.setattr(HARNESS, "_invoke", fail_if_invoked)

    outcome = HARNESS.run_case([], "literal-protocol", str(tmp_path))

    assert outcome["outcome"] == HARNESS.FAIL
    assert outcome["reason"] == "expectation variant 'canonical_names' is missing keys ['programs']"
