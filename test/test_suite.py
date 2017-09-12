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

"OpenQASM conformance test suit. It includes valid and invalid circuits"

import os
import unittest

from .harness import get_file_path, AssertFileMixin

PATH_BASE = os.path.join(os.path.dirname(__file__), "..", "examples")
CATEGORIES = next(os.walk(PATH_BASE))[1]
# To print also the raised errors.
VERBOSE = False

class TestSuite(unittest.TestCase, AssertFileMixin):
    "Test suite"

    def test_suite(self):  # pylint: disable=no-self-use
        "Test runner"

        print("\nOpenQASM conformance test suite\n")

        for category in CATEGORIES:
            filenames = os.listdir(os.path.join(PATH_BASE, category))

            for filename in filenames:
                split = len(filename) - 5
                ext = filename[split + 1:]

                if ext == "qasm":
                    filename_no_ext = filename[:split]

                    self.assertFile(get_file_path(category, filename_no_ext),
                                    VERBOSE, category == "invalid")
