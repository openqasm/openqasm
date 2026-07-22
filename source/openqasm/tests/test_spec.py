import re


from openqasm3.spec import supported_versions


class TestSupportedVersions:
    SPEC_VERSION_RE = r"^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)$"

    def test_supported_versions(self):
        assert supported_versions == ["3.0", "3.1"]

    def test_types(self):
        assert all(type(x) is str for x in supported_versions)  # noqa

    def test_version_formats(self):
        assert all(re.match(self.SPEC_VERSION_RE, x) for x in supported_versions)


def test_parser_version_constants_match_spec():
    """Parser MIN/MAX_SUPPORTED_VERSION are derived from spec.supported_versions."""
    from openqasm3 import spec
    from openqasm3.parser import MIN_SUPPORTED_VERSION, MAX_SUPPORTED_VERSION, _parse_spec_version

    parsed = [_parse_spec_version(v) for v in spec.supported_versions]
    assert MIN_SUPPORTED_VERSION == min(parsed)
    assert MAX_SUPPORTED_VERSION == max(parsed)
