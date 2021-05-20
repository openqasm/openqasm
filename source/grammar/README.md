# OpenQasm 3.0 Grammar

Grammar specification in [ANTLR](https://www.antlr.org/). See `source/grammar/qasm3.g4`.

## Working with ANTLR
To get up and running with ANTLR, follow these steps.
1. Install ANTLR locally following these [instructions](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).
2. Install the ANTLR Python runtime: `pip install antlr4-python3-runtime`.
3. Generate the ANTLR parser files in Python: `antlr4 -Dlanguage=Python3 MYPATH/qasm3.g4`
    - Note: This assumes you set the `antlr4` alias on installation.
4. You can now use the generated files to parse qasm3 code! See, for instance, the method `build_parse_tree()` in `source/grammar/tests/test_grammar`.

## Run the Tests
1. Make sure you are set up with ANTLR by following the steps above.
2. From the root of the repository, run the test suite: `pytest source/grammar/tests/test_grammar.py` (or just `pytest .`)
    - Reference files at `source/grammar/tests/outputs/`
    - Example files at `examples/`
