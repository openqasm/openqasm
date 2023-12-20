import dataclasses

import pytest

import openqasm3
from openqasm3 import ast


def _remove_spans(node):
    """Return a new ``QASMNode`` with all spans recursively set to ``None`` to
    reduce noise in test failure messages."""
    if isinstance(node, list):
        return [_remove_spans(item) for item in node]
    if not isinstance(node, ast.QASMNode):
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


OPERATOR_PRECEDENCE = [
    ast.BinaryOperator["||"],
    ast.BinaryOperator["&&"],
    ast.BinaryOperator["|"],
    ast.BinaryOperator["^"],
    ast.BinaryOperator["&"],
    ast.BinaryOperator["<<"],
    ast.BinaryOperator["+"],
    ast.BinaryOperator["*"],
    ast.BinaryOperator["**"],
]


class TestRoundTrip:
    """All the tests in this class are testing the round-trip properties of the "parse - print -
    parse" operation.  The test cases all need to be written in the preferred output format of the
    printer itself."""

    @pytest.mark.parametrize("indent", ["", "  ", "\t"], ids=repr)
    @pytest.mark.parametrize("chain_else_if", [True, False])
    @pytest.mark.parametrize("old_measurement", [True, False])
    def test_example_files(self, parsed_example, indent, chain_else_if, old_measurement):
        """Test that the cycle 'parse - print - parse' does not affect the generated AST of the
        example files.  Printing should just be an exercise in formatting, so should not affect how
        subsequent runs parse the file.  This also functions as something of a general integration
        test, testing much of the basic surface of the language."""
        roundtrip_ast = openqasm3.parse(
            openqasm3.dumps(
                parsed_example.ast,
                indent=indent,
                chain_else_if=chain_else_if,
                old_measurement=old_measurement,
            )
        )
        assert _remove_spans(roundtrip_ast) == _remove_spans(parsed_example.ast)

    @pytest.mark.parametrize("version_statement", ["OPENQASM 3;", "OPENQASM 3.0;"])
    def test_version(self, version_statement):
        output = openqasm3.dumps(openqasm3.parse(version_statement)).strip()
        assert output == version_statement

    def test_io_declarations(self):
        input_ = """
input int a;
input float[64] a;
input complex[float[FLOAT_WIDTH]] a;
output bit b;
output bit[SIZE] b;
output bool b;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_include(self):
        input_ = 'include "stdgates.inc";'
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_qubit_declarations(self):
        input_ = """
qubit q;
qubit[5] q;
qubit[SIZE] q;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

        old_input = """
qreg q;
qreg q[5];
qreg q[SIZE];
""".strip()
        old_output = openqasm3.dumps(openqasm3.parse(old_input)).strip()
        # Note we're testing that we normalise to the new form.
        assert input_ == old_output

    def test_gate_definition(self):
        input_ = """
gate my_gate q {
}
gate my_gate(param) q {
}
gate my_gate(param1, param2) q {
}
gate my_gate q1, q2 {
}
gate my_gate q {
  x q;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_extern_declaration(self):
        input_ = """
extern f();
extern f() -> bool;
extern f(bool);
extern f(int[32], uint[32]);
extern f(mutable array[complex[float[64]], N_ELEMENTS]) -> int[2 * INT_SIZE];
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_function_declaration(self):
        input_ = """
def f() {
}
def f() -> angle[32] {
  return pi;
}
def f(int[SIZE] a) {
}
def f(qubit q1, qubit[SIZE] q2) {
}
def f(readonly array[int[32], 2] a, mutable array[uint, #dim=2] b) {
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_unary_expression(self):
        input_ = """
!a;
-a;
~(a + a);
-a ** 2;
!true;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_binary_expression(self):
        input_ = """
a * b;
a / b;
1 + 2;
1 - 2;
(1 + 2) * 3;
2 ** 8;
a << 1;
a >> b;
2 < 3;
3 >= 2;
a == b;
a != b;
a & b;
a | b;
a ^ b;
a && b;
a || b;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_assignment(self):
        input_ = """
a = 1;
a = 2 * b;
a = f(4);
a += 1;
a -= a * 0.5;
a *= 2.0;
a /= 1.5;
a **= 2;
a <<= 1;
a >>= 1;
a |= f(2, 3);
a &= "101001";
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_index_expression(self):
        input_ = """
a[0];
a[{1, 2, 3}];
a[0][0];
a[1:2][0];
a[0][1:2];
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_literal(self):
        input_ = """
1;
2.0;
1.0im;
true;
false;
"1010";
"01010";
-1;
1.0ms;
1.0ns;
2.0s;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_declaration(self):
        input_ = """
bool x = true;
bit x;
bit[SIZE] x;
int x = 2;
int[32] x = -5;
uint x = 0;
uint[16] x;
angle x;
angle[SIZE] x;
float x = 2.0;
float[SIZE * 2] x = 4.0;
complex[float[64]] x;
complex z;
duration a = 1.0us;
stretch b;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_const_declaration(self):
        input_ = """
const bool x = true;
const int x = 2;
const int[32] x = -5;
const uint x = 0;
const uint[16] x = 0;
const angle x = pi;
const angle[SIZE] x = pi / 8;
const float x = 2.0;
const float[SIZE * 2] x = 4.0;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_array_initializer(self):
        input_ = """
array[int, 2] a = {1, 2};
array[float[64], 2, 2] a = {{1.0, 0.0}, {0.0, 1.0}};
array[angle[32], 2] a = {pi, pi / 8};
array[uint[16], 4, 4] a = {b, {1, 2, 3, 4}};
array[bool, 2, 2] a = b;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_alias(self):
        input_ = """
let q = a ++ b;
let q = a[1:2];
let q = a[{0, 2, 3}] ++ a[1:1] ++ a[{4, 5}];
let q = a;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_function_call(self):
        input_ = """
f(1, 2, 3);
f();
f(a, b + c, a * b / c);
f(f(a));
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_gate_call(self):
        input_ = """
h q;
h q[0];
gphase(pi);
U(1, 2, 3) q;
U(1, 2, 3) q[0];
my_gate a, b[0:2], c;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_gate_modifiers(self):
        input_ = """
ctrl @ U(1, 2, 3) a, b;
ctrl(1) @ x a, b[0];
negctrl @ U(1, 2, 3) a[0:2], b;
negctrl(2) @ h a, b, c;
pow(2) @ h a;
ctrl @ gphase(pi / 2) a, b;
inv @ h a;
inv @ ctrl @ x a, b;
ctrl(1) @ inv @ x a, b;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_cast(self):
        input_ = """
int(a);
int[32](2.0);
int[SIZE](bitstring);
uint[16 + 16](a);
bit[SIZE](pi);
bool(i);
complex[float[64]](2.0);
complex[float](2.5);
float[32](1);
float(2.0);
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_for_loop(self):
        input_ = """
for uint i in [0:2] {
  a += 1;
}
for int[8] i in [a:b] {
  a += 1;
}
for float[64] i in [a:2 * b:c] {
  a += 1.0;
}
for uint i in {1, 2, 3} {
  a += 1;
}
for int i in {2 * j, 2 + 3 / 4, j + j} {
  a += 1;
}
for complex[float[64]] i in j {
  a += 1;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_while_loop(self):
        input_ = """
while (i) {
  x $0;
  i -= 1;
}
while (i == 0) {
  x $0;
  i -= 1;
}
while (!true) {
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_if(self):
        input_ = """
if (i) {
  x $0;
}
if (true) {
  x $0;
}
if (2 + 3 == 5) {
  x $0;
}
if (!true) {
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_else(self):
        input_ = """
if (true) {
} else {
  x $0;
}
if (true) {
} else {
  x $0;
  a = b + 2;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_else_if(self):
        input_ = """
if (i == 0) {
} else if (i == 1) {
} else {
  x $0;
}
if (i == 0) {
} else if (i == 1) {
  x $0;
} else if (i == 2) {
} else {
  x $1;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_switch_case(self):
        input_ = """
switch (i) {
  case 0 {
    x $0;
  }
  case 1, 2 {
  }
  default {
    z $0;
  }
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_switch_no_default(self):
        input_ = """
switch (i + 1) {
  case 0 {
    x $0;
  }
  case 1, 2 {
  }
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_jumps(self):
        input_ = """
while (true) {
  break;
  continue;
  end;
}
def f() {
  return;
}
def f() -> int[32] {
  return 2 + 3;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_measurement(self):
        input_ = """
measure q;
measure $0;
measure q[0];
measure q[1:3];
c = measure q;
c = measure $0;
c = measure q[0];
c = measure q[1:3];
def f() {
  return measure q;
}
def f() {
  return measure $0;
}
def f() {
  return measure q[0];
}
def f() {
  return measure q[1:3];
}
""".strip()
        output = openqasm3.dumps(
            openqasm3.parse(input_), indent="  ", old_measurement=False
        ).strip()
        assert output == input_

    def test_reset(self):
        input_ = """
reset q;
reset $0;
reset q[0];
reset q[1:3];
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_barrier(self):
        input_ = """
barrier q;
barrier $0;
barrier q[0];
barrier q[1:3];
barrier;
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_delay(self):
        input_ = """
delay[50.0ns] q;
delay[50.0ns] $0;
delay[50.0ns] q[0];
delay[50.0ns] q[1:3];
delay[2 * SIZE] q;
delay[2 * SIZE] $0;
delay[2 * SIZE] q[0];
delay[2 * SIZE] q[1:3];
delay[100.0ns];
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_)).strip()
        assert output == input_

    def test_box(self):
        input_ = """
box {
  x $0;
}
box[100.0ns] {
  x $0;
}
box[a + b] {
  x $0;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_duration_of(self):
        input_ = """
duration a = durationof({
  x $0;
  ctrl @ x $1, $2;
});
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_

    def test_pragma(self):
        input_ = """
pragma blah blah blah
pragma command
pragma !%^* word
""".lstrip()  # The ending newline is important for pragmas.
        output = openqasm3.dumps(openqasm3.parse(input_))
        assert output == input_

    @pytest.fixture(
        params=[
            pytest.param("", id="none"),
            pytest.param("@command\n", id="single"),
            pytest.param("@command keyword\n", id="single keyword"),
            pytest.param("@command !£4&8 hello world\n", id="hard to tokenise"),
            pytest.param("@command1\n@command2 keyword\n", id="multiple"),
        ]
    )
    def annotations(self, request):
        return request.param

    @pytest.mark.parametrize(
        "statement",
        [
            pytest.param("let alias = q[1:3];", id="alias"),
            pytest.param("a = b;", id="assignment"),
            pytest.param("barrier q;", id="barrier"),
            pytest.param("box {\n}", id="box"),
            pytest.param('defcalgrammar "openpulse";', id="defcal"),
            pytest.param("int[8] a;", id="classical declaration"),
            pytest.param("const uint SIZE = 5;", id="const declaration"),
            pytest.param("def f() {\n}", id="subroutine definition"),
            pytest.param("delay[50.0ms] $0;", id="delay"),
            pytest.param("4 * 5 + 3;", id="expression"),
            pytest.param("extern f();", id="extern"),
            pytest.param("for uint i in [0:1] {\n}", id="for"),
            pytest.param("ctrl @ h q;", id="gate call"),
            pytest.param("gphase(0.5);", id="gphase call"),
            pytest.param("gate f q {\n}", id="gate definition"),
            pytest.param("if (true) {\n}", id="if"),
            pytest.param("if (true) {\n} else {\n  1;\n}", id="if-else"),
            pytest.param('include "stdgates.inc";', id="include"),
            pytest.param("input uint[8] i;", id="input declaration"),
            pytest.param("output uint[8] i;", id="output declaration"),
            pytest.param("measure $0;", id="measure"),
            pytest.param("a = measure b;", id="measure assign"),
            pytest.param("qubit[5] q;", id="qubit declaration"),
            pytest.param("reset $0;", id="reset"),
            pytest.param("while (true) {\n}", id="while"),
        ],
    )
    def test_annotations(self, statement, annotations):
        input_ = annotations + statement + "\n"
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ")
        assert output == input_


class TestExpression:
    """Test more specific features and properties of the printer when outputting expressions."""

    @pytest.mark.parametrize(
        "operator", [op for op in ast.BinaryOperator if op != ast.BinaryOperator["**"]]
    )
    def test_associativity_binary(self, operator):
        """Test that the associativity of binary expressions is respected in the output."""
        input_ = ast.Program(
            statements=[
                ast.ExpressionStatement(
                    ast.BinaryExpression(
                        lhs=ast.BinaryExpression(
                            lhs=ast.Identifier("a"),
                            op=operator,
                            rhs=ast.Identifier("b"),
                        ),
                        op=operator,
                        rhs=ast.Identifier("c"),
                    ),
                ),
                ast.ExpressionStatement(
                    ast.BinaryExpression(
                        lhs=ast.Identifier("a"),
                        op=operator,
                        rhs=ast.BinaryExpression(
                            lhs=ast.Identifier("b"),
                            op=operator,
                            rhs=ast.Identifier("c"),
                        ),
                    ),
                ),
            ],
        )
        expected = f"""
a {operator.name} b {operator.name} c;
a {operator.name} (b {operator.name} c);
""".strip()
        output = openqasm3.dumps(input_).strip()
        assert output == expected
        assert openqasm3.parse(output) == input_

    @pytest.mark.xfail(reason="Parser cannot handle bracketed concatenations")
    def test_associativity_concatenation(self):
        """The associativity of concatenation is not fully defined by the grammar or specification,
        but the printer assumes left-associativity for now."""
        input_ = ast.Program(
            statements=[
                ast.AliasStatement(
                    ast.Identifier("q"),
                    ast.Concatenation(
                        lhs=ast.Concatenation(
                            lhs=ast.Identifier("a"),
                            rhs=ast.Identifier("b"),
                        ),
                        rhs=ast.Identifier("c"),
                    ),
                ),
                ast.AliasStatement(
                    ast.Identifier("q"),
                    ast.Concatenation(
                        lhs=ast.Identifier("a"),
                        rhs=ast.Concatenation(
                            lhs=ast.Identifier("b"),
                            rhs=ast.Identifier("c"),
                        ),
                    ),
                ),
            ],
        )
        expected = """
let q = a ++ b ++ c;
let q = a ++ (b ++ c);
""".strip()
        output = openqasm3.dumps(input_).strip()
        assert output == expected
        assert openqasm3.parse(output) == input_

    @pytest.mark.xfail(reason="Currently power is still left-associative in the ANTLR grammar")
    def test_associativity_power(self):
        """Test that the right-associativity of the power expression is respected in the output."""
        input_ = ast.Program(
            statements=[
                ast.ExpressionStatement(
                    ast.BinaryExpression(
                        lhs=ast.BinaryExpression(
                            lhs=ast.Identifier("a"),
                            op=ast.BinaryOperator["**"],
                            rhs=ast.Identifier("b"),
                        ),
                        op=ast.BinaryOperator["**"],
                        rhs=ast.Identifier("c"),
                    ),
                ),
                ast.ExpressionStatement(
                    ast.BinaryExpression(
                        lhs=ast.Identifier("a"),
                        op=ast.BinaryOperator["**"],
                        rhs=ast.BinaryExpression(
                            lhs=ast.Identifier("b"),
                            op=ast.BinaryOperator["**"],
                            rhs=ast.Identifier("c"),
                        ),
                    ),
                ),
            ],
        )
        expected = f"""
(a ** b) ** c;
a ** b ** c;
""".strip()
        output = openqasm3.dumps(input_).strip()
        assert output == expected
        assert openqasm3.parse(output) == input_

    @pytest.mark.parametrize(
        ["lower", "higher"],
        [
            (lower, higher)
            for i, lower in enumerate(OPERATOR_PRECEDENCE[:-1])
            for higher in OPERATOR_PRECEDENCE[i + 1 :]
        ],
    )
    def test_precedence(self, lower, higher):
        input_ = ast.Program(
            statements=[
                ast.ExpressionStatement(
                    ast.BinaryExpression(
                        lhs=ast.BinaryExpression(
                            lhs=ast.Identifier("a"),
                            op=lower,
                            rhs=ast.Identifier("b"),
                        ),
                        op=higher,
                        rhs=ast.BinaryExpression(
                            lhs=ast.Identifier("c"),
                            op=lower,
                            rhs=ast.Identifier("d"),
                        ),
                    ),
                ),
            ],
        )
        expected = f"(a {lower.name} b) {higher.name} (c {lower.name} d);"
        output = openqasm3.dumps(input_).strip()
        assert output == expected
        assert openqasm3.parse(output) == input_


class TestOptions:
    """Test the various keyword arguments to the exporter have the desired effects."""

    @pytest.mark.parametrize("indent", ["", "  ", "\t", "    "], ids=repr)
    def test_indent(self, indent):
        input_ = f"""
def f(int[32] a) -> bool {{
{indent}return a == a;
}}
gate g(param) q {{
{indent}h q;
}}
for uint i in [0:2] {{
{indent}true;
}}
while (i) {{
{indent}i -= 1;
}}
if (i) {{
{indent}x $0;
}} else {{
{indent}x $1;
}}
box {{
{indent}x $0;
}}
durationof({{
{indent}x $0;
}});
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent=indent).strip()
        assert output == input_

    @pytest.mark.parametrize("indent", ["", "  ", "\t", "   "], ids=repr)
    @pytest.mark.parametrize(
        ["outer_start", "outer_end", "allow_classical"],
        [
            pytest.param("gate f q {", "}", False, id="gate"),
            pytest.param("durationof({", "});", False, id="durationof"),
            pytest.param("def f() {", "}", True, id="function"),
            pytest.param("if (true) {", "}", True, id="if"),
            pytest.param("if (true) {\n} else {", "}", True, id="else"),
            pytest.param("box[1.0ms] {", "}", False, id="box"),
        ],
    )
    def test_indent_nested(self, indent, outer_start, outer_end, allow_classical):
        classicals = f"""
for uint i in [0:2] {{
{indent}true;
}}
while (i) {{
{indent}i -= 1;
}}
if (i) {{
{indent}x $0;
}} else {{
{indent}x $1;
}}
durationof({{
{indent}x $0;
}});
""".strip()
        quantums = f"""
box {{
{indent}x $0;
}}
""".strip()
        lines = quantums.splitlines()
        if allow_classical:
            lines.extend(classicals.splitlines())
        input_ = outer_start + "\n" + "\n".join(indent + line for line in lines) + "\n" + outer_end
        output = openqasm3.dumps(openqasm3.parse(input_), indent=indent).strip()
        assert output == input_

    def test_old_measurement(self):
        old_input = "measure q -> c;"
        output = openqasm3.dumps(openqasm3.parse(old_input), old_measurement=True).strip()
        assert output == old_input
        input_ = "c = measure q;"
        output = openqasm3.dumps(openqasm3.parse(input_), old_measurement=True).strip()
        assert output == old_input

    def test_chain_else_if(self):
        input_ = """
if (i == 0) {
} else if (i == 1) {
}
if (i == 0) {
} else if (i == 1) {
} else {
  x $0;
}
if (i == 0) {
} else if (i == 1) {
} else if (i == 2) {
}
if (i == 0) {
} else if (i == 1) {
} else if (i == 2) {
} else {
  if (i == 3) {
  }
  x $0;
}
if (i == 0) {
} else {
  if (i == 2) {
    x $0;
  } else {
    x $0;
  }
  x $0;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ", chain_else_if=True).strip()
        assert output == input_

    def test_no_chain_else_if(self):
        input_ = """
if (i == 0) {
} else {
  if (i == 1) {
  }
}
if (i == 0) {
} else {
  if (i == 1) {
  } else {
    x $0;
  }
}
if (i == 0) {
} else {
  if (i == 1) {
  } else {
    if (i == 2) {
    }
  }
}
if (i == 0) {
} else {
  if (i == 1) {
  } else {
    if (i == 2) {
    } else {
      if (i == 3) {
      }
      x $0;
    }
  }
}
if (i == 0) {
} else {
  if (i == 2) {
    x $0;
  } else {
    x $0;
  }
  x $0;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ", chain_else_if=False).strip()
        assert output == input_

    def test_chain_else_if_only_applies_to_else_if(self):
        input_ = """
if (i) {
} else {
  x $1;
}
if (i) {
} else {
  for uint j in [0:1] {
  }
}
if (i) {
} else {
  x $0;
  if (!i) {
  } else {
    x $1;
  }
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ", chain_else_if=True).strip()
        assert output == input_

    def test_annotations(self):
        input_ = """
@ann_1
int[32] i = 0;
if (i == 0) {
  @ann_2
  i += 1;
}
""".strip()
        output = openqasm3.dumps(openqasm3.parse(input_), indent="  ").strip()
        assert output == input_


def test_CompoundStatement():
    # This test can be replaced with a round trip test once something that
    # parses to a CompoundStatement is implemented (e.g. jakelishman's implementation
    # of the switch statement #492
    cmpnd_stmt = ast.CompoundStatement(
        statements=[
            ast.ExpressionStatement(ast.IntegerLiteral(value=1)),
            ast.ExpressionStatement(ast.IntegerLiteral(value=2)),
        ]
    )
    cmpnd_stmt.annotations = [ast.Annotation(keyword="test_annotation")]
    program = ast.Program(statements=[cmpnd_stmt])

    expected = """
@test_annotation
{
  1;
  2;
}
    """.strip()
    output = openqasm3.dumps(program).strip()
    assert output == expected
