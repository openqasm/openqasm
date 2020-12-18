#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess


CONVERT_COMMAND = 'texi2pdf'


def main(relative_tex_filepath):
    if not os.path.exists(relative_tex_filepath):
        print(
            'File %s does not exist.' % relative_tex_filepath, file=sys.stderr)
        return -1

    absolute_tex_filepath = os.path.abspath(relative_tex_filepath)
    destination_directory = os.path.dirname(absolute_tex_filepath)

    try:
        subprocess.run(
            ['command', '-v', CONVERT_COMMAND]).check_returncode()
    except subprocess.CalledProcessError:
        print('Cannot find `%s`. Ensure you have LaTeX installed and '
              'the command is in the PATH.' % CONVERT_COMMAND, file=sys.stderr)
        return -1

    try:
        subprocess.run(
            [CONVERT_COMMAND, '-c', absolute_tex_filepath],
            cwd=destination_directory)
    except subprocess.CalledProcessError:
        return -1

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: convert2pdf.py path/to/texfile.tex')
        sys.exit(-1)

    sys.exit(main(sys.argv[1]))
