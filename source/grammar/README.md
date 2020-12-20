# OpenQasm 3.0 Grammar

Grammar specification in [ANTLR](https://www.antlr.org/).

Generate parser in Python (run from `openqasm/` root directory):
`antlr4 -Dlanguage=Python3 source/grammar/qasm3.g4`

Run Tests
    - From `openqasm/` root directory, run `python -m unittest source/grammar/tests/test_grammar.py`
    - Reference files at `openqasm/source/grammar/tests/outputs`
    - Example files at `openqasm/examples`
