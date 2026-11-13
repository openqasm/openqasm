"""Conformance tests for include resolution and idempotent inclusion.

Resolution itself is implementation defined, so these tests never assert a lookup algorithm.  They
assert the observable behavior the specification requires, driven by an in-memory resolver whose
contents the test controls completely.

Mapping from each normative statement to its covering test:

===============================================================  ==========================================
Normative statement                                              Covering test
===============================================================  ==========================================
Same target from same includer yields same canonical name        ``test_repeated_target_cannot_change_resolution``
Same canonical name yields same source text                      ``test_canonical_name_cannot_change_source_text``
Relative targets resolve against the includer                    ``test_resolution_is_includer_relative``
Resolution never consults ambient state                          ``test_no_filesystem_access_by_default``
Inclusion cycles must be diagnosed                               ``test_self_inclusion_is_a_cycle``,
                                                                 ``test_mutual_inclusion_is_a_cycle``
Depth beyond what the parser supports is diagnosed               ``test_excessive_inclusion_depth_errors``
No ``.`` or ``..`` path component in an include target           ``test_dot_path_components_rejected``
Source unit incorporated at most once per canonical name         ``test_diamond_incorporates_once``
Rule applies to the whole unit, not only declarations            ``test_once_rule_covers_non_declarations``
Different canonical names are different source units             ``test_two_names_for_same_source_are_two_units``
``defcal`` overloads work across source units                    ``test_defcal_overloads_across_source_units``
Standard library reserved canonical name, no literal file        ``test_standard_library_is_metadata_only``
Non-self-contained units incorporated at first include site      ``test_unit_reading_includer_scope``
An apparent library name is translated through the applicable    ``test_apparent_name_is_translated_through_the_including_map``
library map
Unscoped and scoped library-binding states remain distinct       ``test_library_bindings_are_total_over_their_states``
The includer's own library selects the applicable map            ``test_the_includers_library_selects_the_map``
An unmapped apparent name names no source unit                   ``test_undeclared_library_is_not_reachable_through_a_declared_one``
===============================================================  ==========================================
"""

import dataclasses
import inspect
import os
import re
import unicodedata

import pytest

import openqasm3
from openqasm3 import ast
from openqasm3.ast import Include, QASMNode, QuantumGateDefinition
from openqasm3.filesystem import FileSystemResolver, LibraryResolver
from openqasm3.parser import DEFAULT_SOURCE_NAME
from openqasm3.resolver import (
    AmbiguousIncludeTargetError,
    ChoiceResolver,
    CyclicIncludeError,
    DEFAULT_MAX_INCLUDE_DEPTH,
    DictResolver,
    FunctionResolver,
    IncludeDepthExceededError,
    IncludeError,
    IncludeEnvironment,
    IncludeNotFoundError,
    IncludeResolver,
    InvalidIncludeTargetError,
    InconsistentResolutionError,
    MINIMUM_INCLUDE_DEPTH,
    LIBRARY_PREFIX,
    ROOT_RELATIVE_PREFIX,
    STANDARD_LIBRARY_NAME,
    ResolvedSource,
    StandardLibraryResolver,
    as_resolver,
    library_name,
    library_root,
    validate_library_name,
    validate_source_identity,
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
# Parser include-resolution inputs
# --------------------------------------------------------------------------------------


def test_parse_signature_has_one_include_resolution_input():
    assert tuple(inspect.signature(openqasm3.parse).parameters) == (
        "input_",
        "permissive",
        "ignore_version",
        "includes",
        "name",
    )


def test_default_behavior_does_not_resolve():
    """Parsing without a resolver records only the root source and leaves includes unresolved."""
    program = openqasm3.parse('OPENQASM 3.0;\ninclude "stdgates.inc";')
    (include,) = includes(program)
    assert include.target == "stdgates.inc"
    assert include.canonical_name is None
    assert include.source is None
    assert program.sources == [ast.SourceUnit(DEFAULT_SOURCE_NAME, version="3.0")]


def test_default_behavior_validates_include_targets():
    """Target validity is independent of whether a resolver is supplied."""
    with pytest.raises(InvalidIncludeTargetError, match="path component"):
        openqasm3.parse('include "../g.inc";')


def test_default_behavior_allows_valid_unresolved_targets():
    program = openqasm3.parse('include "lib/g.inc";')
    (include,) = includes(program)
    assert include.target == "lib/g.inc"
    assert include.canonical_name is None
    assert include.source is None
    assert program.sources == [ast.SourceUnit(DEFAULT_SOURCE_NAME)]


def test_mapping_behavior():
    """A mapping of canonical name to source text."""
    program = openqasm3.parse(DIAMOND, includes=DIAMOND_SOURCES, name="main.qasm")
    assert canonical_names(program) == ["main.qasm", "a.inc", "stdgates.inc", "b.inc"]


def test_callable_behavior_returning_pair():
    """A callable returning ``(source, canonical_name)``."""
    seen = []

    def resolve(canonical_name):
        seen.append(canonical_name)
        if canonical_name not in DIAMOND_SOURCES:
            return None
        return DIAMOND_SOURCES[canonical_name], canonical_name

    program = openqasm3.parse('include "a.inc";', includes=resolve, name="main.qasm")
    assert seen == ["a.inc"]
    assert canonical_names(program)[1] == "a.inc"


def test_callable_behavior_returning_bare_string():
    """A callable may return only the source, in which case the name asked for is the identity."""
    seen = []

    def resolve(canonical_name):
        seen.append(canonical_name)
        return "gate solo q { U(0, 0, 0) q; }\n" if canonical_name == "a.inc" else None

    program = openqasm3.parse('include "a.inc";', includes=resolve, name="main.qasm")
    assert seen == ["a.inc"]
    assert canonical_names(program) == ["main.qasm", "a.inc"]


def test_default_source_name_identifies_a_program_parsed_from_a_string():
    """The default name has no prefix, so it contributes no extra candidate."""
    program = openqasm3.parse(
        'include "a.inc";', includes={"a.inc": "gate solo q { U(0, 0, 0) q; }\n"}
    )
    assert canonical_names(program) == [DEFAULT_SOURCE_NAME, "a.inc"]
    assert IncludeEnvironment.unscoped({}).candidates("a.inc", DEFAULT_SOURCE_NAME) == ("a.inc",)


def test_resolver_object_behavior():
    """An :class:`IncludeResolver` instance."""

    class Recording(IncludeResolver):
        def __init__(self):
            self.calls = []

        def lookup(self, canonical_name):
            self.calls.append(canonical_name)
            if canonical_name not in DIAMOND_SOURCES:
                return None
            return ResolvedSource(DIAMOND_SOURCES[canonical_name], canonical_name)

    resolver = Recording()
    openqasm3.parse(DIAMOND, includes=resolver, name="main.qasm")
    assert resolver.calls[0] == "a.inc"
    assert "stdgates.inc" not in resolver.calls


def test_raw_source_backends_agree():
    """The three raw source-backend forms are interchangeable at the call site."""
    source_backends = [
        DIAMOND_SOURCES,
        lambda name: (DIAMOND_SOURCES[name], name) if name in DIAMOND_SOURCES else None,
        DictResolver(DIAMOND_SOURCES),
    ]
    results = [
        canonical_names(openqasm3.parse(DIAMOND, includes=form, name="main.qasm"))
        for form in source_backends
    ]
    assert all(result == results[0] for result in results)


def test_as_resolver_normalizes_each_form():
    assert as_resolver(None) is None
    assert isinstance(as_resolver({}), DictResolver)
    assert isinstance(as_resolver(lambda canonical_name: None), FunctionResolver)
    resolver = DictResolver({})
    assert as_resolver(resolver) is resolver
    with pytest.raises(TypeError, match="must be None, a mapping"):
        as_resolver(7)


def test_choice_resolver_falls_through_on_none():
    """``None`` means "not mine", so the next resolver in the chain is consulted."""
    calls = []

    def declines(canonical_name):
        calls.append(canonical_name)
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


def _library_tree(tmp_path):
    """A vendor library beside a program, each with a same-named file to catch leakage."""
    vendor = tmp_path / "vendor"
    (vendor / "sub").mkdir(parents=True)
    (vendor / "gates.inc").write_text('include "sub/deep.inc";\ngate vendor_gate q { }\n')
    (vendor / "sub" / "deep.inc").write_text('include "//x.inc";\ngate deep q { }\n')
    (vendor / "x.inc").write_text("gate library_x q { }\n")
    program = tmp_path / "program"
    program.mkdir()
    (program / "x.inc").write_text("gate program_x q { }\n")
    (program / "local.inc").write_text("gate local q { }\n")
    resolver = ChoiceResolver([LibraryResolver({"vendor": vendor}), FileSystemResolver([program])])
    return resolver


def test_library_resolver_supplies_a_library_from_disk(tmp_path):
    """The composition that supplies a program from one place and its libraries from another."""
    resolver = _library_tree(tmp_path)
    environment = IncludeEnvironment.scoped(resolver, {"": {"v": "vendor"}})

    program = openqasm3.parse(
        'include "@v/gates.inc";\ninclude "local.inc";',
        includes=environment,
        name="main.qasm",
    )

    gates = gate_names(openqasm3.flatten_includes(program))
    assert "vendor_gate" in gates
    assert "local" in gates


def test_library_resolver_keeps_the_canonical_name_as_the_identity(tmp_path):
    """Returning the canonical name is what keeps a library's own targets inside it."""
    resolver = _library_tree(tmp_path)

    program = openqasm3.parse('include "@vendor/gates.inc";', includes=resolver, name="main.qasm")

    names = canonical_names(program)
    assert "@vendor/gates.inc" in names
    assert "@vendor/sub/deep.inc" in names
    # The library's own ``//x.inc`` reaches its library root, not the program's ``x.inc``.
    assert "@vendor/x.inc" in names
    gates = gate_names(openqasm3.flatten_includes(program))
    assert "library_x" in gates
    assert "program_x" not in gates


def test_library_resolver_declines_what_it_does_not_supply(tmp_path):
    """Declining rather than failing is what lets a resolver be composed."""
    resolver = LibraryResolver({"vendor": tmp_path})

    assert resolver.lookup("@other/gates.inc") is None
    assert resolver.lookup("plain.inc") is None
    assert resolver.lookup("@vendor/absent.inc") is None


def test_library_resolver_refuses_a_file_outside_the_library_root(tmp_path):
    """A symbolic link out of the library is refused, as it is for the file-system resolver."""
    outside = tmp_path / "outside.inc"
    outside.write_text("gate escaped q { }\n")
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    os.symlink(outside, vendor / "escape.inc")

    assert LibraryResolver({"vendor": vendor}).lookup("@vendor/escape.inc") is None


def test_library_resolver_validates_its_library_names(tmp_path):
    """A key that is not a bare library name could never be asked for, so it is rejected."""
    with pytest.raises(ValueError):
        LibraryResolver({"@vendor": tmp_path})
    with pytest.raises(ValueError):
        LibraryResolver({"ven/dor": tmp_path})


def test_library_resolver_reports_an_unreadable_file_rather_than_declining(tmp_path):
    """A file this resolver does supply but cannot decode is a failure, not a miss."""
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    (vendor / "gates.inc").write_bytes(b"\xff\xfe not utf-8")

    with pytest.raises(IncludeError):
        LibraryResolver({"vendor": vendor}).lookup("@vendor/gates.inc")


def test_unresolvable_library_target_names_the_canonical_name_it_tried():
    """A library target that translates but is supplied by nobody reports what was tried.

    A translated library target yields exactly one candidate, so it must not be mistaken for
    a prefixless root and be told to pass ``name=``, which is already set and irrelevant.
    """
    environment = IncludeEnvironment.scoped({}, {"": {"v": "vendor"}})
    with pytest.raises(IncludeNotFoundError) as excinfo:
        openqasm3.parse(
            'include "@v/gates.inc";',
            includes=environment,
            name="main.qasm",
        )
    message = str(excinfo.value)
    assert "@vendor/gates.inc" in message
    assert "no name prefix" not in message
    assert "Pass name=" not in message


def test_unresolvable_library_target_without_maps_omits_the_name_hint():
    """The default, where an apparent name is its own canonical name, reports the same way."""
    with pytest.raises(IncludeNotFoundError) as excinfo:
        openqasm3.parse('include "@v/gates.inc";', includes={}, name="main.qasm")
    message = str(excinfo.value)
    assert "@v/gates.inc" in message
    assert "Pass name=" not in message


def test_unresolvable_target_from_inside_a_library_omits_the_hint():
    """A source unit directly inside a library has a prefix even though it yields one candidate.

    Its includer-relative and library-root candidates coincide, so the hint cannot be selected by
    counting candidates without claiming a library-qualified name has no prefix.
    """
    sources = {"@vendor/gates.inc": 'include "missing.inc";\n'}
    with pytest.raises(IncludeNotFoundError) as excinfo:
        openqasm3.parse('include "@vendor/gates.inc";', includes=sources, name="main.qasm")
    message = str(excinfo.value)
    assert "no name prefix" not in message
    assert "Pass name=" not in message


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

    def resolve(canonical_name):
        nonlocal calls
        calls += 1
        return f"gate g{calls} q {{ U(0, 0, 0) q; }}\n", f"lib{calls}.inc"

    with pytest.raises(IncludeError, match="inconsistent include resolution"):
        openqasm3.parse('include "lib.inc";\ninclude "lib.inc";', includes=resolve)


def test_canonical_name_cannot_change_source_text():
    def resolve(canonical_name):
        name = canonical_name.removesuffix(".inc")
        return f"gate {name} q {{ U(0, 0, 0) q; }}\n", "lib.inc"

    with pytest.raises(IncludeError, match="canonical name 'lib.inc'"):
        openqasm3.parse('include "a.inc";\ninclude "b.inc";', includes=resolve)


def test_candidate_matches_cannot_return_different_text_for_one_canonical_name():
    responses = {
        "lib/x.inc": ("gate first q { U(0, 0, 0) q; }", "shared.inc"),
        "x.inc": ("gate second q { U(0, 0, 0) q; }", "shared.inc"),
    }

    def resolve(canonical_name):
        if canonical_name == "lib/entry.inc":
            return 'include "x.inc";', canonical_name
        return responses.get(canonical_name)

    with pytest.raises(IncludeError, match="canonical name 'shared.inc'"):
        openqasm3.parse('include "lib/entry.inc";', includes=resolve, name="main.qasm")


def test_standard_library_is_metadata_only():
    """Explicit resolution records the reserved source identity without gate declarations."""
    calls = []

    def resolve(canonical_name):
        calls.append(canonical_name)
        return STDGATES, canonical_name

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

    def resolve(canonical_name):
        calls.append(canonical_name)
        return "gate local q { U(0, 0, 0) q; }", canonical_name

    program = openqasm3.parse('include "local.inc";', includes=resolve, name="main.qasm")
    assert calls == ["local.inc"]
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


def test_backslash_in_canonical_name_is_not_a_separator():
    environment = IncludeEnvironment.unscoped({})

    assert environment.candidates("child.inc", r"directory\parent.inc") == ("child.inc",)


def test_ambiguous_target_is_diagnosed_and_disambiguated_by_root_relative_form():
    sources = {
        "lib/util.inc": 'include "shared.inc";\n',
        "lib/shared.inc": "gate near q { U(0, 0, 0) q; }\n",
        "shared.inc": "gate far q { U(0, 0, 0) q; }\n",
    }
    with pytest.raises(AmbiguousIncludeTargetError, match="matches more than one source unit"):
        openqasm3.parse('include "lib/util.inc";', includes=sources, name="main.qasm")

    near = dict(sources, **{"lib/util.inc": 'include "//lib/shared.inc";\n'})
    program = openqasm3.parse('include "lib/util.inc";', includes=near, name="main.qasm")
    assert "lib/shared.inc" in canonical_names(program)
    assert "shared.inc" not in canonical_names(program)

    far = dict(sources, **{"lib/util.inc": 'include "//shared.inc";\n'})
    program = openqasm3.parse('include "lib/util.inc";', includes=far, name="main.qasm")
    assert "shared.inc" in canonical_names(program)
    assert "lib/shared.inc" not in canonical_names(program)


def test_unambiguous_target_resolves_against_the_includer():
    sources = {
        "lib/util.inc": 'include "shared.inc";\n',
        "lib/shared.inc": "gate near q { U(0, 0, 0) q; }\n",
    }
    program = openqasm3.parse('include "lib/util.inc";', includes=sources, name="main.qasm")
    assert "lib/shared.inc" in canonical_names(program)


@pytest.mark.parametrize(
    ("includer", "sources"),
    [
        (
            "main.qasm",
            {
                "lib/util.inc": 'include "shared.inc";\n',
                "lib/shared.inc": "gate near q { U(0, 0, 0) q; }\n",
                "shared.inc": "gate far q { U(0, 0, 0) q; }\n",
            },
        ),
        (
            "@lib/sub/util.inc",
            {
                "@lib/sub/util.inc": 'include "shared.inc";\n',
                "@lib/sub/shared.inc": "gate near q { U(0, 0, 0) q; }\n",
                "@lib/shared.inc": "gate far q { U(0, 0, 0) q; }\n",
            },
        ),
    ],
    ids=["root", "inside-a-library"],
)
def test_ambiguity_remedy_is_a_target_the_author_can_actually_write(includer, sources):
    """Every target the diagnostic offers must validate and resolve to the name it was offered for.

    ``//`` is relative to the includer's library, so inside a library the remedy cannot simply be
    ``//`` joined to the canonical name.
    """
    entry = "@lib/sub/util.inc" if includer.startswith("@") else "lib/util.inc"
    with pytest.raises(AmbiguousIncludeTargetError) as caught:
        openqasm3.parse(f'include "{entry}";', includes=sources, name="main.qasm")

    message = str(caught.value)
    offered = re.findall(r"'([^']+)' or '([^']+)' to say which is meant", message)[0]
    named = re.findall(r"source unit \('([^']+)', '([^']+)'\)", message)[0]

    writer = entry if includer.startswith("@") else "lib/util.inc"
    environment = IncludeEnvironment.unscoped({})
    for remedy, expected in zip(offered, named):
        validate_include_target(remedy, includer=writer)
        assert environment.candidates(remedy, writer) == (expected,)


def test_library_is_hermetic_in_both_directions():
    """A library neither reaches into the including program nor is reached from it by accident."""
    sources = {
        "@lib/gates.inc": 'include "helpers.inc";\n',
        "@lib/helpers.inc": "gate inside q { U(0, 0, 0) q; }\n",
        "helpers.inc": "gate outside q { U(0, 0, 0) q; }\n",
    }
    program = openqasm3.parse(
        'include "@lib/gates.inc";\ninclude "helpers.inc";',
        includes=sources,
        name="main.qasm",
    )
    assert canonical_names(program) == [
        "main.qasm",
        "@lib/gates.inc",
        "@lib/helpers.inc",
        "helpers.inc",
    ]

    without = {name: text for name, text in sources.items() if name != "@lib/helpers.inc"}
    with pytest.raises(IncludeNotFoundError):
        openqasm3.parse('include "@lib/gates.inc";', includes=without, name="main.qasm")

    # The root-relative form is relative to the library, so it cannot name the including program.
    reaching_out = {"@lib/out.inc": 'include "//main.qasm";\n', "main.qasm": "OPENQASM 3.0;\n"}
    with pytest.raises(IncludeNotFoundError):
        openqasm3.parse('include "@lib/out.inc";', includes=reaching_out, name="main.qasm")


def test_inclusion_cycle_is_diagnosed_within_and_across_libraries():
    within = {"@lib/a.inc": 'include "b.inc";\n', "@lib/b.inc": 'include "a.inc";\n'}
    with pytest.raises(CyclicIncludeError, match="@lib/a.inc"):
        openqasm3.parse('include "@lib/a.inc";', includes=within, name="main.qasm")

    across = {"@a/x.inc": 'include "@b/y.inc";\n', "@b/y.inc": 'include "@a/x.inc";\n'}
    with pytest.raises(CyclicIncludeError, match="@a/x.inc"):
        openqasm3.parse('include "@a/x.inc";', includes=across, name="main.qasm")


def test_libraries_may_depend_on_one_another_without_a_source_unit_cycle():
    """Only inclusion cycles are diagnosed; mutual dependence between libraries is not one."""
    sources = {
        "@a/x.inc": 'include "@b/y.inc";\n',
        "@a/w.inc": "gate aw q { U(0, 0, 0) q; }\n",
        "@b/y.inc": "gate by q { U(0, 0, 0) q; }\n",
        "@b/z.inc": 'include "@a/w.inc";\n',
    }
    program = openqasm3.parse(
        'include "@a/x.inc";\ninclude "@b/z.inc";', includes=sources, name="main.qasm"
    )
    assert canonical_names(program) == [
        "main.qasm",
        "@a/x.inc",
        "@b/y.inc",
        "@b/z.inc",
        "@a/w.inc",
    ]


@pytest.mark.parametrize(
    "target",
    ["@", "@lib", "@lib/", "@/name.inc", "//@lib/name.inc", "//"],
)
def test_malformed_library_targets_rejected(target):
    with pytest.raises(InvalidIncludeTargetError):
        validate_include_target(target, includer="lib/main.qasm")


# --------------------------------------------------------------------------------------
# Apparent and canonical library names
# --------------------------------------------------------------------------------------

VENDOR_GATES = "gate vendor_gate q { U(0, 0, 0) q; }\n"
OTHER_GATES = "gate other_gate q { U(0, 0, 0) q; }\n"


@pytest.mark.parametrize(
    ("canonical_name", "expected"),
    [
        ("main.qasm", ""),
        ("lib/main.qasm", ""),
        ("@lib/main.qasm", "lib"),
        ("@lib/sub/main.qasm", "lib"),
        ("@lib", ""),
        (None, ""),
    ],
)
def test_library_name_is_the_library_root_without_its_syntax(canonical_name, expected):
    assert library_name(canonical_name) == expected


@pytest.mark.parametrize(
    ("bindings", "expected"),
    [
        # No map applies, so an apparent name is its own canonical name.
        (None, ["@v/x.inc"]),
        # A map applies and names the library.
        ({"": {"v": "vendor"}}, ["@vendor/x.inc"]),
        ({"": {"v": "v"}}, ["@v/x.inc"]),
        # A map was supplied, so it is strict even when it is empty.
        ({}, []),
        ({"": {}}, []),
        ({"": {"w": "other"}}, []),
        ({"other": {"v": "vendor"}}, []),
    ],
)
def test_library_bindings_are_total_over_their_states(bindings, expected):
    """Unscoped and empty scoped environments are different states."""
    environment = (
        IncludeEnvironment.unscoped({})
        if bindings is None
        else IncludeEnvironment.scoped({}, bindings)
    )

    assert environment.candidates("@v/x.inc", "main.qasm") == tuple(expected)


def test_scoped_environment_uses_the_includers_library_bindings():
    environment = IncludeEnvironment.scoped({}, {"": {"v": "vendor"}})

    assert environment.candidates("@v/x.inc", "main.qasm") == ("@vendor/x.inc",)


def test_environment_resolves_relative_candidates():
    environment = IncludeEnvironment.unscoped({"lib/x.inc": VENDOR_GATES})

    assert environment.resolve("x.inc", "lib/entry.inc") == ResolvedSource(
        VENDOR_GATES, "lib/x.inc"
    )


@pytest.mark.parametrize(
    "source",
    [
        {"x.inc": VENDOR_GATES},
        lambda name: VENDOR_GATES if name == "x.inc" else None,
        DictResolver({"x.inc": VENDOR_GATES}),
    ],
    ids=["mapping", "callable", "resolver"],
)
def test_unscoped_environment_accepts_every_source_backend(source):
    environment = IncludeEnvironment.unscoped(source)

    assert environment.resolve("x.inc", "main.qasm") == ResolvedSource(VENDOR_GATES, "x.inc")


def test_unscoped_environment_preserves_apparent_library_names():
    environment = IncludeEnvironment.unscoped({"@vendor/x.inc": VENDOR_GATES})

    assert environment.candidates("@vendor/x.inc", "main.qasm") == ("@vendor/x.inc",)


def test_scoped_environment_snapshots_nested_bindings():
    bindings = {"": {"v": "vendor"}}
    environment = IncludeEnvironment.scoped({}, bindings)

    bindings[""]["v"] = "other"
    bindings["vendor"] = {"v": "other"}

    assert environment.candidates("@v/x.inc", "main.qasm") == ("@vendor/x.inc",)
    assert environment.candidates("@v/x.inc", "@vendor/entry.inc") == ()


@pytest.mark.parametrize(
    "bindings",
    [
        [],
        {"": []},
        {"bad/owner": {}},
        {"": {"bad/name": "vendor"}},
        {"": {"v": "@vendor"}},
    ],
)
def test_scoped_environment_rejects_malformed_bindings(bindings):
    with pytest.raises((TypeError, ValueError)):
        IncludeEnvironment.scoped({}, bindings)


def test_environment_requires_a_source_backend():
    with pytest.raises(TypeError, match="must supply source lookup"):
        IncludeEnvironment.unscoped(None)


def test_environment_reserves_the_standard_library_before_the_backend():
    calls = []

    def resolve(canonical_name):
        calls.append(canonical_name)
        return VENDOR_GATES

    environment = IncludeEnvironment.unscoped(resolve)

    assert environment.resolve(STANDARD_LIBRARY_NAME, "main.qasm") == ResolvedSource(
        "", STANDARD_LIBRARY_NAME
    )
    assert calls == []


def test_environment_coalesces_candidates_with_one_source_identity():
    responses = {
        "lib/x.inc": ResolvedSource(VENDOR_GATES, "shared.inc"),
        "x.inc": ResolvedSource(VENDOR_GATES, "shared.inc"),
    }
    environment = IncludeEnvironment.unscoped(responses.get)

    assert environment.resolve("x.inc", "lib/entry.inc") == ResolvedSource(
        VENDOR_GATES, "shared.inc"
    )


def test_environment_rejects_different_text_for_one_source_identity():
    responses = {
        "lib/x.inc": ResolvedSource(VENDOR_GATES, "shared.inc"),
        "x.inc": ResolvedSource(OTHER_GATES, "shared.inc"),
    }
    environment = IncludeEnvironment.unscoped(responses.get)

    with pytest.raises(InconsistentResolutionError) as caught:
        environment.resolve("x.inc", "lib/entry.inc")

    assert caught.value.identity == "include-resolution-inconsistent-source"


def test_environment_rejects_ambiguous_source_identities():
    environment = IncludeEnvironment.unscoped({"lib/x.inc": VENDOR_GATES, "x.inc": OTHER_GATES})

    with pytest.raises(AmbiguousIncludeTargetError, match="write '//lib/x.inc' or '//x.inc'"):
        environment.resolve("x.inc", "lib/entry.inc")


def test_ambiguity_remedies_use_candidates_not_opaque_source_identities():
    responses = {
        "lib/x.inc": ResolvedSource(VENDOR_GATES, "mem://near"),
        "x.inc": ResolvedSource(OTHER_GATES, "mem://far"),
    }
    environment = IncludeEnvironment.unscoped(responses.get)

    with pytest.raises(AmbiguousIncludeTargetError) as caught:
        environment.resolve("x.inc", "lib/entry.inc")

    assert "('mem://near', 'mem://far')" in str(caught.value)
    assert "write '//lib/x.inc' or '//x.inc'" in str(caught.value)
    assert environment.resolve("//lib/x.inc", "lib/entry.inc").canonical_name == "mem://near"
    assert environment.resolve("//x.inc", "lib/entry.inc").canonical_name == "mem://far"


def test_empty_scoped_environment_diagnoses_an_unavailable_library():
    environment = IncludeEnvironment.scoped({}, {})

    with pytest.raises(IncludeNotFoundError, match="no library named 'v'"):
        environment.resolve("@v/x.inc", "main.qasm")


def test_the_includers_library_selects_the_map():
    maps = {"": {"v": "root_choice"}, "lib": {"v": "library_choice"}}
    environment = IncludeEnvironment.scoped({}, maps)
    assert environment.candidates("@v/x.inc", "main.qasm") == ("@root_choice/x.inc",)
    assert environment.candidates("@v/x.inc", "sub/main.qasm") == ("@root_choice/x.inc",)
    assert environment.candidates("@v/x.inc", DEFAULT_SOURCE_NAME) == ("@root_choice/x.inc",)
    assert environment.candidates("@v/x.inc", "@lib/g.inc") == ("@library_choice/x.inc",)
    assert environment.candidates("@v/x.inc", "@lib/sub/g.inc") == ("@library_choice/x.inc",)


def test_library_bindings_do_not_affect_other_target_forms():
    maps = {"": {"v": "vendor"}, "lib": {"v": "vendor"}}
    environment = IncludeEnvironment.scoped({}, maps)
    assert environment.candidates("x.inc", "lib/main.qasm") == ("lib/x.inc", "x.inc")
    assert environment.candidates(ROOT_RELATIVE_PREFIX + "x.inc", "@lib/sub/g.inc") == (
        "@lib/x.inc",
    )
    assert environment.candidates(STANDARD_LIBRARY_NAME, "@lib/g.inc") == (STANDARD_LIBRARY_NAME,)


def test_no_library_map_leaves_apparent_names_canonical():
    """The supported path for a host that does not scope library names."""
    sources = {"@vendor/gates.inc": VENDOR_GATES}
    program = openqasm3.parse('include "@vendor/gates.inc";', includes=sources, name="main.qasm")
    assert canonical_names(program) == ["main.qasm", "@vendor/gates.inc"]


def test_apparent_name_is_translated_through_the_including_map():
    sources = {"@vendor/gates.inc": VENDOR_GATES}
    environment = IncludeEnvironment.scoped(sources, {"": {"v": "vendor"}})
    program = openqasm3.parse(
        'include "@v/gates.inc";',
        includes=environment,
        name="main.qasm",
    )
    assert canonical_names(program) == ["main.qasm", "@vendor/gates.inc"]


def test_two_apparent_names_for_one_library_name_one_source_unit():
    """One library reached under two spellings is one canonical name, so it is incorporated once."""
    sources = {
        "@vendor/gates.inc": VENDOR_GATES,
        "@liba/use.inc": 'include "@c/gates.inc";\n',
        "@libb/use.inc": 'include "@see/gates.inc";\n',
    }
    maps = {
        "": {"a": "liba", "b": "libb"},
        "liba": {"c": "vendor"},
        "libb": {"see": "vendor"},
    }
    environment = IncludeEnvironment.scoped(sources, maps)
    program = openqasm3.parse(
        'include "@a/use.inc";\ninclude "@b/use.inc";',
        includes=environment,
        name="main.qasm",
    )
    assert canonical_names(program) == [
        "main.qasm",
        "@liba/use.inc",
        "@vendor/gates.inc",
        "@libb/use.inc",
    ]
    assert gate_names(openqasm3.flatten_includes(program)).count("vendor_gate") == 1


def test_one_apparent_name_for_two_libraries_stays_distinct():
    """Two libraries may use one spelling for different libraries without colliding."""
    sources = {
        "@vendor/gates.inc": VENDOR_GATES,
        "@other/gates.inc": OTHER_GATES,
        "@liba/use.inc": 'include "@c/gates.inc";\n',
        "@libb/use.inc": 'include "@c/gates.inc";\n',
    }
    maps = {
        "": {"a": "liba", "b": "libb"},
        "liba": {"c": "vendor"},
        "libb": {"c": "other"},
    }
    environment = IncludeEnvironment.scoped(sources, maps)
    program = openqasm3.parse(
        'include "@a/use.inc";\ninclude "@b/use.inc";',
        includes=environment,
        name="main.qasm",
    )
    assert canonical_names(program) == [
        "main.qasm",
        "@liba/use.inc",
        "@vendor/gates.inc",
        "@libb/use.inc",
        "@other/gates.inc",
    ]


def test_undeclared_library_is_not_reachable_through_a_declared_one():
    """A library's own libraries are not the using program's; visibility is not transitive."""
    sources = {
        "@util/u.inc": "gate util_gate q { U(0, 0, 0) q; }\n",
        "@liba/use.inc": 'include "@util/u.inc";\n',
    }
    maps = {"": {"liba": "liba"}, "liba": {"util": "util"}}
    environment = IncludeEnvironment.scoped(sources, maps)
    program = openqasm3.parse('include "@liba/use.inc";', includes=environment, name="main.qasm")
    assert "@util/u.inc" in canonical_names(program)

    with pytest.raises(IncludeNotFoundError, match="no library named 'util'"):
        openqasm3.parse('include "@util/u.inc";', includes=environment, name="main.qasm")


def test_a_library_with_no_map_entry_reaches_no_library():
    """A library that was given no libraries of its own resolves no library target."""
    sources = {
        "@vendor/gates.inc": VENDOR_GATES,
        "@liba/use.inc": 'include "@vendor/gates.inc";\n',
    }
    maps = {"": {"liba": "liba"}}
    environment = IncludeEnvironment.scoped(sources, maps)
    with pytest.raises(IncludeNotFoundError, match="no library named 'vendor'"):
        openqasm3.parse('include "@liba/use.inc";', includes=environment, name="main.qasm")


def test_a_library_map_does_not_reach_the_standard_library_reservation():
    """The reservation is matched before any map, so a library still reaches it."""
    sources = {"@vendor/gates.inc": 'include "stdgates.inc";\n' + VENDOR_GATES}
    environment = IncludeEnvironment.scoped(sources, {"": {"v": "vendor"}, "vendor": {}})
    program = openqasm3.parse(
        'include "@v/gates.inc";',
        includes=environment,
        name="main.qasm",
    )
    assert canonical_names(program) == ["main.qasm", "@vendor/gates.inc", "stdgates.inc"]


def test_the_documented_scoped_environment_example_behaves_as_documented():
    """The scoped example printed in the API documentation, including what it refuses."""
    libraries = {
        "@vendor/gates.inc": 'include "@h/helpers.inc";',
        "@helpers/helpers.inc": "gate flip q { U(pi, 0, pi) q; }",
    }
    maps = {"": {"v": "vendor"}, "vendor": {"h": "helpers"}}
    environment = IncludeEnvironment.scoped(DictResolver(libraries), maps)
    program = openqasm3.parse(
        'include "@v/gates.inc";',
        includes=environment,
        name="main.qasm",
    )
    assert canonical_names(program) == ["main.qasm", "@vendor/gates.inc", "@helpers/helpers.inc"]

    # The program reaches @vendor/ only because its own map names it, under either spelling.
    for undeclared in ('include "@h/helpers.inc";', 'include "@helpers/helpers.inc";'):
        with pytest.raises(IncludeNotFoundError):
            openqasm3.parse(undeclared, includes=environment, name="main.qasm")


def test_include_target_is_readable_under_its_deprecated_name():
    include = Include(target="lib/g.inc")
    assert include.target == "lib/g.inc"
    with pytest.deprecated_call():
        assert include.filename == "lib/g.inc"


def test_include_can_be_constructed_with_its_deprecated_name():
    with pytest.deprecated_call():
        include = Include(filename="lib/g.inc")

    assert include.target == "lib/g.inc"
    assert "filename" not in {item.name for item in dataclasses.fields(include)}


def test_include_deprecated_name_can_be_assigned():
    include = Include(target="lib/old.inc")

    with pytest.deprecated_call():
        include.filename = "lib/new.inc"

    assert include.target == "lib/new.inc"


def test_include_can_be_replaced_with_its_deprecated_name():
    include = Include(target="lib/old.inc", canonical_name="lib/old.inc", source=1)

    with pytest.deprecated_call():
        replaced = dataclasses.replace(include, filename="lib/new.inc")

    assert replaced.target == "lib/new.inc"
    assert replaced.canonical_name == "lib/old.inc"
    assert replaced.source == 1


def test_deprecated_include_name_takes_precedence_when_both_are_supplied():
    with pytest.deprecated_call():
        include = Include(target="lib/old.inc", filename="lib/new.inc")

    assert include.target == "lib/new.inc"


@pytest.mark.parametrize(
    ("canonical_name", "expected"),
    [
        ("main.qasm", ""),
        ("lib/main.qasm", ""),
        ("@lib/main.qasm", "@lib/"),
        ("@lib/sub/main.qasm", "@lib/"),
        ("@lib", ""),
        ("lib/@lib/main.qasm", ""),
        (None, ""),
    ],
)
def test_library_root_is_derived_from_the_name_alone(canonical_name, expected):
    assert library_root(canonical_name) == expected


@pytest.mark.parametrize(
    ("target", "includer", "expected"),
    [
        # A root-name-space includer contributes its directory prefix and the bare name.
        ("x.inc", "main.qasm", ["x.inc"]),
        ("x.inc", "lib/main.qasm", ["lib/x.inc", "x.inc"]),
        # The root-relative form names one candidate, which is what resolves an ambiguity.
        (ROOT_RELATIVE_PREFIX + "x.inc", "lib/main.qasm", ["x.inc"]),
        (ROOT_RELATIVE_PREFIX + "lib/x.inc", "lib/main.qasm", ["lib/x.inc"]),
        # A library bounds the fallback, so a source unit in one cannot reach another.
        ("x.inc", "@lib/gates.inc", ["@lib/x.inc"]),
        ("x.inc", "@lib/sub/gates.inc", ["@lib/sub/x.inc", "@lib/x.inc"]),
        (ROOT_RELATIVE_PREFIX + "x.inc", "@lib/sub/gates.inc", ["@lib/x.inc"]),
        # An explicit library target names one candidate from anywhere.
        (LIBRARY_PREFIX + "other/x.inc", "main.qasm", ["@other/x.inc"]),
        (LIBRARY_PREFIX + "other/x.inc", "@lib/gates.inc", ["@other/x.inc"]),
        # The reserved standard-library name is never scoped to a library.
        (STANDARD_LIBRARY_NAME, "main.qasm", [STANDARD_LIBRARY_NAME]),
        (STANDARD_LIBRARY_NAME, "lib/main.qasm", [STANDARD_LIBRARY_NAME]),
        (STANDARD_LIBRARY_NAME, "@lib/gates.inc", [STANDARD_LIBRARY_NAME]),
        (STANDARD_LIBRARY_NAME, "@lib/sub/gates.inc", [STANDARD_LIBRARY_NAME]),
    ],
)
def test_environment_candidates_follow_the_specified_rule(target, includer, expected):
    environment = IncludeEnvironment.unscoped({})

    assert environment.candidates(target, includer) == tuple(expected)


def test_standard_library_resolver_supplies_only_the_reserved_name():
    resolver = StandardLibraryResolver()
    reserved = resolver.lookup("stdgates.inc")
    assert reserved == ResolvedSource("", "stdgates.inc")
    assert resolver.lookup("lib/stdgates.inc") is None
    assert resolver.lookup("other.inc") is None


def test_a_library_can_include_the_standard_library():
    """The reservation is what lets a library use the standard library at all."""
    sources = {"@lib/gates.inc": 'include "stdgates.inc";\ngate g q { U(0, 0, 0) q; }\n'}
    program = openqasm3.parse('include "@lib/gates.inc";', includes=sources, name="main.qasm")
    assert canonical_names(program) == ["main.qasm", "@lib/gates.inc", "stdgates.inc"]


def test_filesystem_resolver_declines_library_names(tmp_path):
    """Resolved paths cannot carry a library prefix, so the resolver declines rather than
    silently resolving a library name into an ordinary one."""
    (tmp_path / "@lib").mkdir()
    (tmp_path / "@lib" / "gates.inc").write_text("gate g q { U(0, 0, 0) q; }\n")
    resolver = FileSystemResolver([tmp_path])
    assert resolver.lookup("@lib/gates.inc") is None
    with pytest.raises(IncludeNotFoundError):
        openqasm3.parse('include "@lib/gates.inc";', includes=resolver, name="main.qasm")


def test_filesystem_resolver_absolute_identity_is_accepted_as_opaque(tmp_path):
    source = tmp_path / "gates.inc"
    source.write_text("gate g q { U(0, 0, 0) q; }\n")

    program = openqasm3.parse('include "gates.inc";', includes=FileSystemResolver([tmp_path]))

    expected = str(source.resolve()).replace("\\", "/")
    assert canonical_names(program) == [DEFAULT_SOURCE_NAME, expected]


@pytest.mark.parametrize(
    ("target", "expected_gate", "forbidden_gate"),
    [
        ("@vendor/gates.inc", "from_library", "from_disk_helpers"),
        ("local.inc", "from_disk", "from_library"),
    ],
)
def test_recommended_library_composition_resolves_both_sources(
    tmp_path, target, expected_gate, forbidden_gate
):
    """The composition :class:`FileSystemResolver` recommends for hosts that supply libraries.

    The mapping supplies libraries, which the file-system resolver declines, and the file system
    supplies everything else.  The library stays hermetic: its own ``helpers.inc`` resolves within
    the library even though a different ``helpers.inc`` sits in the search root.
    """
    (tmp_path / "local.inc").write_text("gate from_disk q { U(0, 0, 0) q; }\n")
    (tmp_path / "helpers.inc").write_text("gate from_disk_helpers q { U(0, 0, 0) q; }\n")
    libraries = {
        "@vendor/gates.inc": 'include "helpers.inc";\n',
        "@vendor/helpers.inc": "gate from_library q { U(0, 0, 0) q; }\n",
    }
    resolver = ChoiceResolver([DictResolver(libraries), FileSystemResolver([tmp_path])])

    program = openqasm3.parse(f'include "{target}";', includes=resolver, name="main.qasm")

    gates = gate_names(openqasm3.flatten_includes(program))
    assert expected_gate in gates
    assert forbidden_gate not in gates


@pytest.mark.parametrize(
    "source",
    ["// only a comment\n", "\n   \n", ""],
    ids=["comment-only", "whitespace-only", "empty"],
)
def test_source_unit_with_no_statements_is_incorporated(source):
    """A source unit matching no tokens has no stop token, which once broke span construction."""
    program = openqasm3.parse(
        'OPENQASM 3.0;\ninclude "u.inc";', includes={"u.inc": source}, name="main.qasm"
    )
    assert canonical_names(program) == ["main.qasm", "u.inc"]
    assert program.sources[1].statements == []


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


def test_filesystem_resolver_wraps_decode_errors(tmp_path):
    (tmp_path / "bad.inc").write_bytes(b"\x80")

    with pytest.raises(IncludeError) as excinfo:
        openqasm3.parse('include "bad.inc";', includes=FileSystemResolver([tmp_path]))

    assert isinstance(excinfo.value.__cause__, UnicodeDecodeError)


def test_filesystem_resolver_wraps_unknown_encoding(tmp_path):
    (tmp_path / "source.inc").write_text("")

    with pytest.raises(IncludeError) as excinfo:
        openqasm3.parse(
            'include "source.inc";',
            includes=FileSystemResolver([tmp_path], encoding="not-a-codec"),
        )

    assert isinstance(excinfo.value.__cause__, LookupError)


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
    """This parser's own depth guarantee; the specification leaves any limit implementation defined."""
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

    def explode(canonical_name):
        raise AssertionError("resolver must not be consulted for an invalid target")

    with pytest.raises(InvalidIncludeTargetError):
        openqasm3.parse('include "../g.inc";', includes=explode)


def test_absolute_target_never_reaches_the_resolver():
    """A resolver that would happily open an absolute path is never given the chance."""

    def explode(canonical_name):
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


def test_mapping_prefers_an_exact_match_over_a_normalized_one():
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


def test_mapping_rejects_ambiguous_normalized_fallback():
    first = "a\u0301\u0323.inc"
    second = "a\u0323\u0301.inc"
    query = unicodedata.normalize("NFC", first)
    assert query not in (first, second)

    resolver = DictResolver({first: "first", second: "second"})
    with pytest.raises(AmbiguousIncludeTargetError, match="Normalization Form C"):
        resolver.lookup(query)


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

    def synthesize(canonical_name):
        if canonical_name == "stdgates.inc":
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


def _reachable_spanned_nodes(root):
    stack = [root]
    seen = set()
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, QASMNode):
            if current.span is not None:
                yield current
            stack.extend(current.__dict__.values())
        elif isinstance(current, (list, tuple)):
            stack.extend(current)


def test_spans_carry_their_source_unit():
    program = openqasm3.parse(
        'bit root;\ninclude "nested.inc";',
        includes={"nested.inc": "gate nested(theta) q { U(theta, 0, 0) q; }"},
        name="main.qasm",
    )
    included_index = canonical_names(program).index("nested.inc")
    root_nodes = list(_reachable_spanned_nodes(program.statements))
    included_nodes = list(_reachable_spanned_nodes(program.sources[included_index].statements))

    assert root_nodes
    assert included_nodes
    assert all(node.span.source == 0 for node in root_nodes)
    assert all(node.span.source == included_index for node in included_nodes)
    assert all(0 <= node.span.source < len(program.sources) for node in root_nodes + included_nodes)


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


def test_every_public_name_is_importable():
    """``__all__`` is the advertised surface, so every name in it must actually resolve."""
    missing = [name for name in openqasm3.__all__ if not hasattr(openqasm3, name)]
    assert missing == []


@pytest.mark.parametrize(
    "name",
    [
        "main.qasm",
        "/absolute/main.qasm",
        "../workspace/main.qasm",
        "back\\slash.qasm",
        "mem://workspace/main.qasm",
    ],
)
def test_a_root_source_identity_is_opaque(name):
    assert openqasm3.parse("OPENQASM 3.0;", name=name).sources[0].canonical_name == name


@pytest.mark.parametrize(("identity", "error"), [("", ValueError), (17, TypeError)])
def test_a_source_identity_must_be_a_nonempty_string(identity, error):
    with pytest.raises(error):
        validate_source_identity(identity)

    with pytest.raises(error):
        openqasm3.parse("OPENQASM 3.0;", name=identity)


def test_a_virtual_resolver_identity_is_accepted_without_interpretation():
    identity = "mem://workspace/includes/gates.inc"
    program = openqasm3.parse(
        'OPENQASM 3.0; include "gates.inc";',
        includes=lambda _: ("gate g q {}", identity),
        name="mem://workspace/main.qasm",
    )

    assert program.sources[1].canonical_name == identity


@pytest.mark.parametrize(("identity", "error"), [("", ValueError), (17, TypeError)])
def test_a_resolver_identity_must_be_a_nonempty_string(identity, error):
    with pytest.raises(error):
        openqasm3.parse(
            'OPENQASM 3.0; include "gates.inc";',
            includes=lambda _: ("gate g q {}", identity),
        )


@pytest.mark.parametrize(
    "bindings",
    [
        {"bad/owner": {}},
        {17: {}},
        {"": {"": "valid"}},
        {"": {"bad/name": "valid"}},
        {"": {"@bad": "valid"}},
        {"": {".": "valid"}},
        {"": {"..": "valid"}},
        {"": {"bad*": "valid"}},
        {"": {"bad?": "valid"}},
        {"": {17: "valid"}},
        {"": {"valid": ""}},
        {"": {"valid": "bad\\name"}},
        {"": {"valid": "@bad"}},
        {"": {"valid": 17}},
    ],
)
def test_environment_bindings_reject_malformed_bare_names(bindings):
    with pytest.raises((TypeError, ValueError)):
        IncludeEnvironment.scoped({}, bindings)


def test_library_names_allow_square_and_curly_brackets():
    assert validate_library_name("vendor[1]{stable}") == "vendor[1]{stable}"
    environment = IncludeEnvironment.scoped({}, {"owner[1]": {"apparent{2}": "canonical[3]"}})
    program = openqasm3.parse(
        "OPENQASM 3.0;",
        includes=environment,
    )
    assert program.sources[0].canonical_name == DEFAULT_SOURCE_NAME


def test_an_identity_may_be_supplied_when_a_class_covers_several_faults():
    """One mechanism across the package: a class-level default that a raise site may override."""
    assert IncludeError("boom").identity is None
    assert IncludeError("boom", identity="custom").identity == "custom"
    assert IncludeNotFoundError("boom").identity == "include-not-found"
    assert IncludeNotFoundError("boom", identity="custom").identity == "custom"


def test_a_resolver_that_answers_one_name_two_ways_is_refused():
    """Resolution must be a function of the target, or a program has no settled meaning."""
    texts = iter(["gate g q { U(0, 0, 0) q; }", "gate h q { U(0, 0, 0) q; }"])

    with pytest.raises(InconsistentResolutionError) as caught:
        openqasm3.parse(
            'OPENQASM 3.0; include "a.inc"; include "a.inc";',
            includes=lambda name: next(texts, ""),
        )
    assert caught.value.identity.startswith("include-resolution-inconsistent")


def test_flattening_keeps_an_include_whose_source_index_names_nothing():
    """Only reachable for a hand-built program, where dropping it would lose the caller's data."""
    statement = openqasm3.ast.Include(target="ghost.inc")
    statement.source = 99
    program = openqasm3.ast.Program(statements=[statement], version="3.0")
    program.sources = [openqasm3.ast.SourceUnit(canonical_name="<input>")]

    flattened = openqasm3.flatten_includes(program)
    assert [type(node) for node in flattened.statements] == [openqasm3.ast.Include]


def test_every_resolver_export_is_re_exported_by_the_package():
    """A caller writing a resolver should not have to learn which half of the API moved."""
    missing = sorted(set(openqasm3.resolver.__all__) - set(openqasm3.__all__))
    assert missing == []
    unbound = sorted(name for name in openqasm3.__all__ if not hasattr(openqasm3, name))
    assert unbound == []


@pytest.mark.parametrize(
    ("error", "identity"),
    [
        (IncludeNotFoundError, "include-not-found"),
        (CyclicIncludeError, "include-cycle"),
        (IncludeDepthExceededError, "include-depth-exceeded"),
        (InvalidIncludeTargetError, "include-target-invalid"),
        (AmbiguousIncludeTargetError, "include-target-ambiguous"),
    ],
)
def test_include_errors_carry_a_stable_identity(error, identity):
    """The identity is the portable contract, so it belongs to the exception, not to a caller."""
    assert error.identity == identity
    assert error("message").identity == identity


def test_the_base_include_error_has_no_identity():
    """It is raised for inconsistent resolution, which has no agreed identity to report."""
    assert IncludeError.identity is None
