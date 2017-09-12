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

"""Helpers."""

import os

from qiskit import qasm


def get_file_path(category, file_name):
    """
        ie: examples/generic/adder.qasm
        - category: "generic"
        - file_name: "adder"
    """

    return os.path.join(os.path.dirname(__file__), "../examples", category, file_name + ".qasm")


def parse(file_path, prec=15):
    """
      - file_path: Path to the OpenQASM file
      - prec: Precision for the returned string
    """

    qiskit_qasm = qasm.Qasm(file_path)

    try:
        qiskit_qasm.parse().qasm(prec)
        return True
    except qasm.QasmError:
        return False


class AssertFileMixin(object):  # pylint: disable=too-few-public-methods
    """
    Provides an "assertFile" assertion that checks for the parseability of
    the provided file.
    """
    @staticmethod
    def assertFile(file_path, invalid=False):  # pylint: disable=invalid-name
        """
        Custom asserts for QASM files.
        - file_path: Path to the OpenQASM file
        - invalid: If we´re checking an invalid files
        """
        if not parse(file_path) and not invalid:
            raise AssertionError("TODO: Parse from QASM file:" + file_path)
