import sys
import re


def parse_versions():
    with open(sys.argv[2], "r") as version_file:
        for line in version_file:
            comment_start = line.find("#")
            if comment_start >= 0:
                line = line[: line.find("#")]
            line = line.strip()
            if not line:
                continue
            version_parts = tuple(int(x) for x in line.split("."))
            yield version_parts[0], version_parts[1]


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {__file__} path/to/setup.cfg path/to/antlr_versions.txt", file=sys.stderr)
        sys.exit(1)

    versions = sorted(parse_versions())
    if not versions:
        print("didn't receive any versions to support", file=sys.stderr)
        sys.exit(2)
    if versions[0][0] != 4 or versions[-1][0] != 4:
        print("can only handle ANTLR 4", file=sys.stderr)
        sys.exit(4)
    min_minor = versions[0][1]
    max_minor = versions[-1][1]
    if {minor for _, minor in versions} != set(range(min_minor, max_minor + 1)):
        print("supplied minor versions must be continuous", file=sys.stderr)
        sys.exit(8)
    constraint = f"antlr4_python3_runtime>=4.{min_minor},<4.{max_minor + 1}"
    with open(sys.argv[1], "r") as setup_file:
        contents = setup_file.read()
    new_contents, count = re.subn(
        r"antlr4-python3-runtime\s*#\s*__ANTLR_VERSIONS__", constraint, contents
    )
    if not count:
        print("given setup.cfg file did not seem to contain an antlr4 dependency", file=sys.stderr)
        sys.exit(16)
    with open(sys.argv[1], "w") as setup_file:
        setup_file.write(new_contents)


if __name__ == "__main__":
    main()
