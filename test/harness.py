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


def parse(file_path, verbose=False, prec=15):
    """
      - file_path: Path to the OpenQASM file
      - prec: Precision for the returned string
    """

    qiskit_qasm = qasm.Qasm(file_path)

    try:
        qiskit_qasm.parse().qasm(prec)
        return True
    except qasm.QasmError as err:
        if verbose:
            print("Error:")
            print(err)
        return False


def get_value(line):
    """
      - line: Line with QASM code to inspect
    """
    return line.split(":")[1].strip()


class AssertFileMixin(object):  # pylint: disable=too-few-public-methods
    """
    Provides an "assertFile" assertion that checks for the parseability of
    the provided file.
    """
    @staticmethod
    def assertFile(file_path, verbose=False, invalid=False):  # pylint: disable=invalid-name
        """
        Custom asserts for QASM files.
        - file_path: Path to the OpenQASM file
        - invalid: If we´re checking an invalid file
        """
        # TODO: We need to read the file twice because the parser still does not
        # support to receive strings. But we need the header here.
        src = open(file_path, "r")
        lines = src.readlines()
        src.close()

        name = None
        section = None

        for line in lines:
            if "//" in line:
                if "name:" in line:
                    name = get_value(line)
                if "section:" in line:
                    section = get_value(line)
                    # We can stop looking for metadata at this point
                    break

        category = os.path.basename(os.path.dirname(file_path))
        msg = " - "
        # If the file doesn´t include metadata we use the real name
        # to get some info
        if not name:
            msg = msg + os.path.splitext(os.path.basename(file_path))[0]
        else:
            msg = msg + name
            if section:
                msg = msg + ", section: " + section

        msg = msg + " (" + category + ")"

        print(msg)

        res = parse(file_path, verbose)
        if (not res and not invalid) or (res and invalid):
            raise AssertionError(msg)
