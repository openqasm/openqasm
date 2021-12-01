import os
import pytest

from openqasm.parser.antlr.qasm_parser import parse


class TestOpenQasmTests:
    """Test the example and tests from the openqasm project"""

    @pytest.fixture(scope="function", autouse=True)
    def setup(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))  # tests/ dir
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(test_dir)))  # project root dir
        self.examples_path = os.path.join(root_dir, "examples/")

    def test_examples(self):
        """Loop through all example files, verify that the ast_parser can parse the file.

        Examples located at: ``openqasm/examples``.
        """
        examples = os.listdir(self.examples_path)
        success_count = 0
        fail_count = 0
        for e in examples:
            if e.endswith(".qasm"):
                example_file = os.path.join(self.examples_path, e)
                with open(example_file) as f:
                    source = f.read()
                    try:
                        parse(source)
                        print(f"success: {example_file}")
                        success_count += 1
                    except Exception as e:
                        print(f"fail: {example_file}\n{e}")
                        fail_count += 1
                        # raise

        if fail_count > 0:  # Should pass all 21
            raise Exception(f"{success_count} succeed and {fail_count} failed.")
