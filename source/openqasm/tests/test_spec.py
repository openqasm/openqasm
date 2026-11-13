import re


from openqasm3.parser import (
    DEFAULT_VERSION,
    _SUPPORTED_VERSIONS,
    _normalize_version,
    _parse_spec_version,
)
from openqasm3.spec import supported_versions


class TestSupportedVersions:
    SPEC_VERSION_RE = r"^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)$"

    def test_supported_versions(self):
        assert supported_versions == ["3.0", "3.1", "3.2"]

    def test_types(self):
        assert all(type(x) is str for x in supported_versions)  # noqa

    def test_version_formats(self):
        assert all(re.match(self.SPEC_VERSION_RE, x) for x in supported_versions)

    def test_parser_supported_versions_match_spec(self):
        parsed_versions = frozenset(
            _normalize_version(_parse_spec_version(version)) for version in supported_versions
        )
        assert DEFAULT_VERSION == (3, 0)
        assert _SUPPORTED_VERSIONS == parsed_versions
