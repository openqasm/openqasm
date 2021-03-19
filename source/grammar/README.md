# OpenQasm 3.0 Grammar

Grammar specification in [ANTLR](https://www.antlr.org/).

Generate ANTLR parser in Python: `antlr4 -Dlanguage=Python3 MYPATH/qasm3.g4`

Run Tests
    - Run the test suite: `pytest MYPATH/test_grammar.py` (or just `pytest`). The `test_grammar.py`
    file is located at: `openqasm/source/grammar/tests/test_grammar.py`.
    - Reference files at `openqasm/source/grammar/tests/outputs/`
    - Example files at `openqasm/examples/`
