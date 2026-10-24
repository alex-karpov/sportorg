import pytest

from sportorg_ng import __version__
from sportorg_ng.core.version import Version


def test_package_version_parses() -> None:
    assert str(Version.parse(__version__)) == __version__


@pytest.mark.parametrize("text", ["1.2", "a.b.c", "1.-2.3", ""])
def test_parse_rejects_malformed(text: str) -> None:
    with pytest.raises(
        ValueError, match=r"expected MAJOR\.MINOR\.PATCH|invalid literal|non-negative"
    ):
        _ = Version.parse(text)
