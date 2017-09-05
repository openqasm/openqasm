"""Entry point for the OpenQASM test conformance suite."""
import unittest

class TestExample(unittest.TestCase):
    """Example test."""

    def test_upper(self):
        """Example method."""
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()
