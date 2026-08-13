"""Conformance tests for include resolution and idempotent inclusion.

Resolution itself is implementation defined, so these tests never assert a lookup algorithm.  They
assert the observable behaviour the specification requires, driven by an in-memory resolver whose
contents the test controls completely.

Mapping from each normative statement to its covering test:

===============================================================  ==========================================
Normative statement                                              Covering test
===============================================================  ==========================================
Same target from same includer yields same canonical name        ``test_repeated_target_is_stable``
Same canonical name yields same source text                      ``test_diamond_incorporates_once``
Relative targets resolve against the includer                    ``test_resolution_is_includer_relative``
Resolution never consults ambient state                          ``test_no_filesystem_access_by_default``
Inclusion cycles must be diagnosed                               ``test_self_inclusion_is_a_cycle``,
                                                                 ``test_mutual_inclusion_is_a_cycle``
Inclusion depth of at least 15 supported                         ``test_minimum_inclusion_depth_supported``
Depth beyond what the parser supports is diagnosed               ``test_excessive_inclusion_depth_errors``
No ``.`` or ``..`` path component in an include target           ``test_dot_path_components_rejected``
Source unit incorporated at most once per canonical name         ``test_diamond_incorporates_once``
Rule applies to the whole unit, not only declarations            ``test_once_rule_covers_non_declarations``
Different canonical names are different source units             ``test_two_names_for_same_source_are_two_units``
``defcal`` overloads work across source units                    ``test_defcal_overloads_across_source_units``
Standard library reserved canonical name, no literal file        ``test_standard_library_is_metadata_only``
Non-self-contained units incorporated at first include site      ``test_unit_reading_includer_scope``
===============================================================  ==========================================
"""

import dataclasses
import unicodedata

import pytest

import openqasm3
from openqasm3 import ast
from openqasm3.ast import Include, QASMNode, QuantumGateDefinition
from openqasm3.filesystem import FileSystemResolver
from openqasm3.parser import DEFAULT_SOURCE_NAME
from openqasm3.resolver import (
    ChoiceResolver,
    CyclicIncludeError,
    DEFAULT_MAX_INCLUDE_DEPTH,
    DictResolver,
    FunctionResolver,
    IncludeDepthExceededError,
    IncludeError,
    IncludeNotFoundError,
    IncludeResolver,
    InvalidIncludeTargetError,
    MINIMUM_INCLUDE_DEPTH,
    ResolvedSource,
    as_resolver,
    validate_include_target,
)

STDGATES = "gate h q { U(pi/2, 0, pi) q; }\ngate x q { U(pi, 0, pi) q; }\n"
LIBRARY_A = 'include "stdgates.inc";\ngate my_a q { h q; }\n'
LIBRARY_B = 'include "stdgates.inc";\ngate my_b q { x q; }\n'
DIAMOND = 'OPENQASM 3.0;\ninclude "a.inc";\ninclude "b.inc";\n'
DIAMOND_SOURCES = {"stdgates.inc": STDGATES, "a.inc": LIBRARY_A, "b.inc": LIBRARY_B}


def gate_names(program):
    return [
        statement.name.name
        for statement in program.statements
        if isinstance(statement, QuantumGateDefinition)
    ]


def canonical_names(program):
    return [unit.canonical_name for unit in program.sources]


def includes(program):
    return [statement for statement in program.statements if isinstance(statement, Include)]


# --------------------------------------------------------------------------------------
# The four load behaviours
# --------------------------------------------------------------------------------------


def test_default_behaviour_does_not_resolve():
    """Parsing without a resolver is unchanged from before this feature existed."""
    program = openqasm3.parse('OPENQASM 3.0;\ninclude "stdgates.inc";')
    (include,) = includes(program)
    assert include.filename == "stdgates.inc"
    assert include.canonical_name is None
    assert include.source is None
    assert program.sources == []


def test_default_behaviour_validates_include_targets():
    """Target validity is independent of whether a resolver is supplied."""
    with pytest.raises(InvalidIncludeTargetError, match="path component"):
        openqasm3.parse('include "../g.inc";')


def test_default_behaviour_allows_valid_unresolved_targets():
    program = openqasm3.parse('include "lib/g.inc";')
    (include,) = includes(program)
    assert include.filename == "lib/g.inc"
    assert include.canonical_name is None
    assert include.source is None
    assert program.sources == []


def test_mapping_behaviour():
    """A mapping of canonical name to source text."""
    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    assert canonical_names(program) == ["main.qasm", "a.inc", "stdgates.inc", "b.inc"]


def test_callable_behaviour_returning_pair():
    """A callable returning ``(source, canonical_name)``."""
    seen = []

    def resolve(target, includer):
        seen.append((target, includer))
        return DIAMOND_SOURCES[target], target

    program = openqasm3.parse('include "a.inc";', includes=resolve, name="main.qasm")
    assert seen == [("a.inc", "main.qasm")]
    assert canonical_names(program)[1] == "a.inc"


def test_callable_behaviour_returning_bare_string():
    """A callable may return only the source, in which case the target is the canonical name."""
    program = openqasm3.parse('include "stdgates.inc";', includes=lambda target, includer: STDGATES)
    assert canonical_names(program) == [DEFAULT_SOURCE_NAME, "stdgates.inc"]


def test_resolver_object_behaviour():
    """An :class:`IncludeResolver` instance."""

    class Recording(IncludeResolver):
        def __init__(self):
            self.calls = []

        def resolve(self, target, includer):
            self.calls.append((target, includer))
            return ResolvedSource(DIAMOND_SOURCES[target], target)

    resolver = Recording()
    openqasm3.parse(DIAMOND, includes=resolver, name="main.qasm")
    assert resolver.calls[0] == ("a.inc", "main.qasm")
    assert ("stdgates.inc", "a.inc") not in resolver.calls


def test_all_four_behaviours_agree():
    """The four forms are interchangeable at the call site."""
    resolver_forms = [
        DIAMOND_SOURCES,
        lambda target, includer: (DIAMOND_SOURCES[target], target),
        DictResolver(DIAMOND_SOURCES),
        ChoiceResolver([DictResolver(DIAMOND_SOURCES)]),
    ]
    results = [
        canonical_names(openqasm3.parse(DIAMOND, includes=form, name="main.qasm"))
        for form in resolver_forms
    ]
    assert all(result == results[0] for result in results)


def test_as_resolver_normalises_each_form():
    assert as_resolver(None) is None
    assert isinstance(as_resolver({}), DictResolver)
    assert isinstance(as_resolver(lambda target, includer: None), FunctionResolver)
    resolver = DictResolver({})
    assert as_resolver(resolver) is resolver
    with pytest.raises(TypeError, match="must be None, a mapping"):
        as_resolver(7)


def test_choice_resolver_falls_through_on_none():
    """``None`` means "not mine", so the next resolver in the chain is consulted."""
    calls = []

    def declines(target, includer):
        calls.append(target)
        return None

    resolver = ChoiceResolver([FunctionResolver(declines), DictResolver({"other.inc": STDGATES})])
    program = openqasm3.parse('include "other.inc";', includes=resolver)
    assert calls == ["other.inc"]
    assert canonical_names(program)[1] == "other.inc"


def test_unresolvable_target_raises():
    with pytest.raises(IncludeNotFoundError, match="nope.inc"):
        openqasm3.parse('include "nope.inc";', includes={})


def test_unresolvable_target_from_prefixless_root_hints_at_name():
    """A caller who omitted ``name=`` is told why includer-relative resolution did nothing."""
    with pytest.raises(IncludeNotFoundError, match="no name prefix") as excinfo:
        openqasm3.parse('include "nope.inc";', includes={})
    assert "Pass name=" in str(excinfo.value)


def test_unresolvable_target_from_prefixed_includer_omits_the_hint():
    """The hint is noise when the includer does have a prefix, so it is not emitted."""
    sources = {"lib/util.inc": 'include "missing.inc";\n'}
    with pytest.raises(IncludeNotFoundError) as excinfo:
        openqasm3.parse('include "lib/util.inc";', includes=sources, name="main.qasm")
    assert "no name prefix" not in str(excinfo.value)
    assert "lib/util.inc" in str(excinfo.value)


# --------------------------------------------------------------------------------------
# The observable resolution contract
# --------------------------------------------------------------------------------------


def test_repeated_target_is_stable():
    """The same target from the same includer resolves to the same canonical name."""
    source = 'include "stdgates.inc";\ninclude "stdgates.inc";'
    program = openqasm3.parse(source, includes={"stdgates.inc": STDGATES})
    first, second = includes(program)
    assert first.canonical_name == second.canonical_name == "stdgates.inc"
    assert first.source == second.source


def test_repeated_target_cannot_change_resolution():
    calls = 0

    def resolve(target, includer):
        nonlocal calls
        calls += 1
        return f"gate g{calls} q {{ U(0, 0, 0) q; }}\n", f"lib{calls}.inc"

    with pytest.raises(IncludeError, match="inconsistent include resolution"):
        openqasm3.parse('include "lib.inc";\ninclude "lib.inc";', includes=resolve)


def test_canonical_name_cannot_change_source_text():
    def resolve(target, includer):
        name = target.removesuffix(".inc")
        return f"gate {name} q {{ U(0, 0, 0) q; }}\n", "lib.inc"

    with pytest.raises(IncludeError, match="canonical name 'lib.inc'"):
        openqasm3.parse('include "a.inc";\ninclude "b.inc";', includes=resolve)


def test_standard_library_is_metadata_only():
    """Explicit resolution records the reserved source identity without gate declarations."""
    calls = []

    def resolve(target, includer):
        calls.append((target, includer))
        return STDGATES, target

    program = openqasm3.parse(
        'OPENQASM 3.1;\ninclude "stdgates.inc";\n', includes=resolve, name="main.qasm"
    )
    (include,) = includes(program)
    unit = program.sources[include.source]
    assert calls == []
    assert unit.canonical_name == "stdgates.inc"
    assert unit.statements == []
    assert unit.version is None
    assert gate_names(openqasm3.flatten_includes(program)) == []


def test_standard_library_does_not_override_other_targets():
    calls = []

    def resolve(target, includer):
        calls.append((target, includer))
        return "gate local q { U(0, 0, 0) q; }", target

    program = openqasm3.parse('include "local.inc";', includes=resolve, name="main.qasm")
    assert calls == [("local.inc", "main.qasm")]
    assert gate_names(openqasm3.flatten_includes(program)) == ["local"]


def test_resolution_is_includer_relative():
    sources = {
        "lib/gates/extra.inc": 'include "helpers.inc";\n',
        "lib/gates/helpers.inc": "gate hh q { U(0, 0, 0) q; }\n",
    }
    program = openqasm3.parse('include "lib/gates/extra.inc";', includes=sources, name="main.qasm")
    assert canonical_names(program) == [
        "main.qasm",
        "lib/gates/extra.inc",
        "lib/gates/helpers.inc",
    ]


def test_includer_prefix_takes_precedence_over_bare_target():
    sources = {
        "lib/util.inc": 'include "shared.inc";\n',
        "lib/shared.inc": "gate near q { U(0, 0, 0) q; }\n",
        "shared.inc": "gate far q { U(0, 0, 0) q; }\n",
    }
    program = openqasm3.parse('include "lib/util.inc";', includes=sources, name="main.qasm")
    assert "lib/shared.inc" in canonical_names(program)
    assert "shared.inc" not in canonical_names(program)


def test_bare_target_used_when_no_includer_prefix_matches():
    """A target that is not found beside its includer falls back to its own name.

    This is what allows a nested library to reach the standard library.
    """
    sources = {
        "lib/util.inc": 'include "stdgates.inc";\n',
        "stdgates.inc": STDGATES,
    }
    program = openqasm3.parse('include "lib/util.inc";', includes=sources, name="main.qasm")
    assert "stdgates.inc" in canonical_names(program)


def test_no_filesystem_access_by_default(monkeypatch, tmp_path):
    """Resolution never consults the process working directory or the file system.

    A root parsed from a string has no name prefix, so a target that no resolver supplies fails
    with :class:`IncludeNotFoundError` rather than being looked up on disk.
    """

    def explode(*args, **kwargs):
        raise AssertionError("include resolution must not touch the file system")

    monkeypatch.setattr("builtins.open", explode)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helpers.inc").write_text("gate g q { U(0, 0, 0) q; }\n")

    openqasm3.parse('include "helpers.inc";')
    with pytest.raises(IncludeNotFoundError):
        openqasm3.parse('include "helpers.inc";', includes={})


def test_filesystem_resolver_rejects_symlink_escape(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "escaped.inc").write_text("gate escaped q { U(0, 0, 0) q; }\n")
    try:
        (root / "escaped.inc").symlink_to(outside / "escaped.inc")
    except OSError as exc:
        pytest.skip(f"could not create symlink fixture: {exc}")

    with pytest.raises(IncludeNotFoundError, match="escaped.inc"):
        openqasm3.parse('include "escaped.inc";', includes=FileSystemResolver([root]))


def test_filesystem_resolver_keeps_nested_includes_in_selected_root(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    (first / "dir").mkdir(parents=True)
    (second / "dir").mkdir(parents=True)
    (first / "dir" / "child.inc").write_text("gate from_first q { U(0, 0, 0) q; }\n")
    (second / "dir" / "parent.inc").write_text('include "child.inc";\n')
    (second / "dir" / "child.inc").write_text("gate from_second q { U(0, 0, 0) q; }\n")

    program = openqasm3.parse(
        'include "dir/parent.inc";', includes=FileSystemResolver([first, second])
    )

    assert gate_names(openqasm3.flatten_includes(program)) == ["from_second"]


def test_self_inclusion_is_a_cycle():
    with pytest.raises(CyclicIncludeError, match="cycle"):
        openqasm3.parse('include "x.inc";', includes={"x.inc": 'include "x.inc";'})


def test_mutual_inclusion_is_a_cycle():
    sources = {"x.inc": 'include "y.inc";', "y.inc": 'include "x.inc";'}
    with pytest.raises(CyclicIncludeError, match="x.inc"):
        openqasm3.parse('include "x.inc";', includes=sources)


def _chain(depth):
    sources = {f"f{index}.inc": f'include "f{index + 1}.inc";\n' for index in range(depth)}
    sources[f"f{depth}.inc"] = "gate leaf q { U(0, 0, 0) q; }\n"
    return sources


def test_minimum_inclusion_depth_supported():
    """The specification requires support for an inclusion depth of at least 15."""
    assert DEFAULT_MAX_INCLUDE_DEPTH >= MINIMUM_INCLUDE_DEPTH
    program = openqasm3.parse('include "f0.inc";', includes=_chain(MINIMUM_INCLUDE_DEPTH))
    assert "leaf" in gate_names(openqasm3.flatten_includes(program))


def test_excessive_inclusion_depth_errors():
    with pytest.raises(IncludeDepthExceededError, match="inclusion depth"):
        openqasm3.parse('include "f0.inc";', includes=_chain(DEFAULT_MAX_INCLUDE_DEPTH + 5))


@pytest.mark.parametrize("target", ["./g.inc", "../g.inc", "lib/./g.inc", "lib/../g.inc"])
def test_dot_path_components_rejected(target):
    with pytest.raises(InvalidIncludeTargetError, match="path component"):
        openqasm3.parse(f'include "{target}";', includes={target: ""})


@pytest.mark.parametrize(
    "target,reason",
    [
        ("/etc/passwd", "absolute"),
        ("/g.inc", "absolute"),
        (r"lib\g.inc", r"'\\' character"),
        (r"\\server\share\g.inc", r"'\\' character"),
        ("C:/lib/g.inc", "drive specifier"),
        ("c:g.inc", "drive specifier"),
        ("lib//g.inc", "empty path component"),
    ],
)
def test_non_portable_targets_rejected(target, reason):
    """Forms whose meaning differs between host systems are rejected, not merely unresolved."""
    with pytest.raises(InvalidIncludeTargetError, match=reason):
        openqasm3.parse(f'include "{target}";', includes={target: ""})


def test_empty_target_rejected():
    """Unreachable from source, since the grammar's string literal needs one character."""
    with pytest.raises(InvalidIncludeTargetError, match="is empty"):
        validate_include_target("")
    with pytest.raises(openqasm3.parser.QASM3ParsingError):
        openqasm3.parse('include "";')


def test_a_backslash_target_is_a_literal_backslash():
    """OpenQASM strings have no escape sequences, so this is a well-formed token."""
    with pytest.raises(InvalidIncludeTargetError):
        openqasm3.parse(r'include "a\tb.inc";')


def test_dot_check_precedes_the_resolver():
    """The prohibition is enforced centrally, so a host resolver cannot bypass it."""

    def explode(target, includer):
        raise AssertionError("resolver must not be consulted for an invalid target")

    with pytest.raises(InvalidIncludeTargetError):
        openqasm3.parse('include "../g.inc";', includes=explode)


def test_absolute_target_never_reaches_the_resolver():
    """A resolver that would happily open an absolute path is never given the chance."""

    def explode(target, includer):
        raise AssertionError("resolver must not be consulted for an invalid target")

    with pytest.raises(InvalidIncludeTargetError):
        openqasm3.parse('include "/etc/passwd";', includes=explode)


def test_mapping_matches_a_target_under_nfc():
    """A decomposed target reaches a precomposed name, so hosts agree across file systems."""
    precomposed = unicodedata.normalize("NFC", "caf\u00e9.inc")
    decomposed = unicodedata.normalize("NFD", precomposed)
    assert precomposed != decomposed

    program = openqasm3.parse(
        f'OPENQASM 3.0;\ninclude "{decomposed}";',
        includes={precomposed: "gate cafe q { U(0, 0, 0) q; }"},
        name="main.qasm",
    )
    assert [unit.canonical_name for unit in program.sources] == ["main.qasm", precomposed]


def test_mapping_prefers_an_exact_match_over_a_normalised_one():
    precomposed = unicodedata.normalize("NFC", "caf\u00e9.inc")
    decomposed = unicodedata.normalize("NFD", precomposed)

    program = openqasm3.parse(
        f'OPENQASM 3.0;\ninclude "{decomposed}";',
        includes={
            precomposed: "gate a q { U(0, 0, 0) q; }",
            decomposed: "gate b q { U(0,0,0) q; }",
        },
        name="main.qasm",
    )
    assert [unit.canonical_name for unit in program.sources] == ["main.qasm", decomposed]


# --------------------------------------------------------------------------------------
# Incorporating a source unit
# --------------------------------------------------------------------------------------


def test_diamond_incorporates_once():
    """Two libraries that each include the standard library can be combined."""
    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    flattened = openqasm3.flatten_includes(program)
    names = gate_names(flattened)
    assert names == ["my_a", "my_b"]
    assert canonical_names(program).count("stdgates.inc") == 1


def test_second_include_points_at_the_same_source_unit():
    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    stdgates_index = canonical_names(program).index("stdgates.inc")
    unit_a = program.sources[canonical_names(program).index("a.inc")]
    unit_b = program.sources[canonical_names(program).index("b.inc")]
    for unit in (unit_a, unit_b):
        (include,) = [s for s in unit.statements if isinstance(s, Include)]
        assert include.source == stdgates_index


def test_once_rule_covers_non_declarations():
    """The rule applies to the whole source unit, not only to its declarations."""
    sources = {
        "noisy.inc": "pragma vendor.thing on\ngate n q { U(0, 0, 0) q; }\n",
        "one.inc": 'include "noisy.inc";\n',
        "two.inc": 'include "noisy.inc";\n',
    }
    program = openqasm3.parse(
        'include "one.inc";\ninclude "two.inc";', includes=sources, name="main.qasm"
    )
    flattened = openqasm3.flatten_includes(program)
    pragmas = [s for s in flattened.statements if isinstance(s, ast.Pragma)]
    assert len(pragmas) == 1


def test_two_names_for_same_source_are_two_units():
    """The specification makes no promise about physical identity, only canonical names."""
    body = "gate dup q { U(0, 0, 0) q; }\n"
    sources = {"one.inc": body, "two.inc": body}
    program = openqasm3.parse(
        'include "one.inc";\ninclude "two.inc";', includes=sources, name="main.qasm"
    )
    assert canonical_names(program) == ["main.qasm", "one.inc", "two.inc"]
    assert gate_names(openqasm3.flatten_includes(program)).count("dup") == 2


def test_defcal_overloads_across_source_units():
    """``defcal`` statements from different source units overload normally."""
    sources = {
        "cal_q0.inc": "defcal rx $0 {}\n",
        "cal_q1.inc": "defcal rx $1 {}\n",
    }
    program = openqasm3.parse(
        'include "cal_q0.inc";\ninclude "cal_q1.inc";', includes=sources, name="main.qasm"
    )
    flattened = openqasm3.flatten_includes(program)
    definitions = [s for s in flattened.statements if isinstance(s, ast.CalibrationDefinition)]
    assert [d.name.name for d in definitions] == ["rx", "rx"]


def test_standard_library_is_incorporated_once():
    """``stdgates.inc`` needs no literal file; the canonical name is what matters."""

    def synthesize(target, includer):
        if target == "stdgates.inc":
            raise AssertionError("the caller resolver must not receive stdgates.inc")
        return None

    resolver = ChoiceResolver(
        [FunctionResolver(synthesize), DictResolver({"a.inc": LIBRARY_A, "b.inc": LIBRARY_B})]
    )
    program = openqasm3.parse(DIAMOND, includes=resolver, name="main.qasm")
    assert canonical_names(program).count("stdgates.inc") == 1
    assert program.sources[canonical_names(program).index("stdgates.inc")].statements == []


def test_unit_reading_includer_scope():
    """A source unit that reads its includer's scope is incorporated at the first include site.

    This documents the accepted consequence of the once rule rather than asserting an error.
    """
    sources = {"defs.inc": "int j = i + 5;\n"}
    program = openqasm3.parse(
        'int i = 100;\ninclude "defs.inc";\ninclude "defs.inc";',
        includes=sources,
        name="main.qasm",
    )
    flattened = openqasm3.flatten_includes(program)
    declarations = [
        s
        for s in flattened.statements
        if isinstance(s, ast.ClassicalDeclaration) and s.identifier.name == "j"
    ]
    assert len(declarations) == 1


# --------------------------------------------------------------------------------------
# Source identity, printing, and visitors
# --------------------------------------------------------------------------------------


def test_spans_carry_their_source_unit():
    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    assert all(statement.span.source == 0 for statement in program.statements if statement.span)
    stdgates_index = canonical_names(program).index("stdgates.inc")
    unit = program.sources[stdgates_index]
    assert all(
        statement.span.source == stdgates_index for statement in unit.statements if statement.span
    )


def test_printer_never_emits_resolved_content():
    resolved = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    unresolved = openqasm3.parse(DIAMOND)
    assert openqasm3.dumps(resolved) == openqasm3.dumps(unresolved)
    assert "my_a" not in openqasm3.dumps(resolved)


def test_resolution_does_not_change_program_identity():
    """Resolution annotates a program; it never changes what the program is.

    This is the same guarantee the printer and the generic visitor make, expressed for equality.
    """
    resolved = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    unresolved = openqasm3.parse(DIAMOND)
    assert resolved == unresolved
    assert _remove_spans(resolved) == _remove_spans(unresolved)


def test_round_trip_with_resolution_enabled():
    """Parse, print, reparse and compare, matching how the repository defines round-tripping."""
    resolved = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    reparsed = openqasm3.parse(
        openqasm3.dumps(resolved), includes=DIAMOND_SOURCES, name="main.qasm"
    )
    assert _remove_spans(resolved) == _remove_spans(reparsed)


def test_generic_visitor_does_not_traverse_resolved_content():
    """Enabling resolution must not silently change what existing visitors see."""

    class Counter(openqasm3.visitor.QASMVisitor):
        def __init__(self):
            self.count = 0

        def visit_QuantumGateDefinition(self, node, context=None):
            self.count += 1

    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    counter = Counter()
    counter.visit(program)
    assert counter.count == 0

    flattened_counter = Counter()
    flattened_counter.visit(openqasm3.flatten_includes(program))
    assert flattened_counter.count == 2


def test_included_version_statement_is_retained_not_applied():
    sources = {"versioned.inc": "OPENQASM 3.0;\ngate v q { U(0, 0, 0) q; }\n"}
    program = openqasm3.parse(
        'OPENQASM 3.1;\ninclude "versioned.inc";', includes=sources, name="main.qasm"
    )
    assert program.version == "3.1"
    unit = program.sources[canonical_names(program).index("versioned.inc")]
    assert unit.version == "3.0"


def _remove_spans(node):
    """Return a new ``QASMNode`` with all spans recursively set to ``None``.

    This is the same helper used by ``test_qasm_parser.py``.  Include provenance needs no special
    handling here because it is declared ``compare=False``.
    """
    if isinstance(node, list):
        return [_remove_spans(item) for item in node]
    if not isinstance(node, QASMNode):
        return node
    kwargs = {}
    no_init = {}
    for field in dataclasses.fields(node):
        if field.name == "span":
            continue
        target = kwargs if field.init else no_init
        target[field.name] = _remove_spans(getattr(node, field.name))
    out = type(node)(**kwargs)
    for attribute, value in no_init.items():
        setattr(out, attribute, value)
    return out
