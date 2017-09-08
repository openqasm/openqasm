# -*- coding: utf-8 -*-

# Copyright 2017 IBM RESEARCH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""Conformance tests for invalid circuits."""

import unittest

from qiskit.qasm import QasmError

from utils import parse
from utils import get_file_path


CATEGORY = "invalid"


class TestParser(unittest.TestCase):
    "Invalid circuits"


    def test_missing_semicolon(self):
        "Missing semicolon"

        # TODO: Abstract these assertions ("harness").
        self.assertRaisesRegex(QasmError,
                               "Error at end of file. Perhaps there is a missing ';'",
                               parse,
                               file_path=get_file_path(CATEGORY, "missing_semicolon"))


    def test_gate_no_found(self):
        "NO existent gate"

        self.assertRaisesRegex(QasmError,
                               "Cannot find gate definition for 'w'",
                               parse,
                               file_path=get_file_path(CATEGORY, "gate_no_found"))


if __name__ == '__main__':
    unittest.main()
