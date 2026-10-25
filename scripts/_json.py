"""Typed JSON and https helpers for the measurement scripts (stdlib only).

``json.loads`` returns ``Any``; the helpers here narrow untyped JSON values with
``isinstance`` so that the scripts stay fully typed without casts or suppressions.
"""

import json
import tomllib
import urllib.request
from typing import IO, TYPE_CHECKING, Protocol, TypeGuard
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

type Json = dict[str, Json] | list[Json] | str | int | float | bool | None

_HTTPS = "https"


class _Open(Protocol):
    """Shape of ``OpenerDirector.open`` with a concrete (non-``Any``) return type."""

    def __call__(
        self, fullurl: str, data: bytes | None = None, timeout: float = ...
    ) -> IO[bytes]: ...


# Declaring the callable type is the single sanctioned place where ``Any`` is narrowed.
_LOADS: Callable[[str | bytes], Json] = json.loads
# TOML without dates (pyproject.toml, uv.lock, Cargo.lock) is a JSON value.
_TOML_LOADS: Callable[[str], Json] = tomllib.loads


def _opener(headers: Mapping[str, str] | None) -> _Open:
    opener = urllib.request.build_opener()
    opener.addheaders = list((headers or {}).items())
    return opener.open


def _is_dict(value: object) -> TypeGuard[dict[str, Json]]:
    """JSON objects always have ``str`` keys, so a ``dict`` is a ``dict[str, Json]``."""
    return isinstance(value, dict)


def _is_list(value: object) -> TypeGuard[list[Json]]:
    return isinstance(value, list)


def parse_json(text: str | bytes) -> Json:
    """Parse JSON text into a typed ``Json`` value."""
    result: Json = _LOADS(text)
    return result


def parse_toml(text: str) -> Json:
    """Parse TOML text (without dates) into a typed ``Json`` value."""
    result: Json = _TOML_LOADS(text)
    return result


def as_dict(value: object) -> dict[str, Json]:
    """Return ``value`` if it is a JSON object, otherwise an empty dict."""
    return value if _is_dict(value) else {}


def as_list(value: object) -> list[Json]:
    """Return ``value`` if it is a JSON array, otherwise an empty list."""
    return value if _is_list(value) else []


def as_str(value: object, default: str = "") -> str:
    """Return ``value`` if it is a string, otherwise ``default``."""
    return value if isinstance(value, str) else default


def as_int(value: object, default: int = 0) -> int:
    """Return ``value`` if it is an int (not a bool), otherwise ``default``."""
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value


def as_float(value: object, default: float = 0.0) -> float:
    """Return ``value`` as a float if it is a number (not a bool), otherwise ``default``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return float(value)


def as_opt_float(value: object) -> float | None:
    """Return ``value`` as a float if it is a number, otherwise ``None``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def fetch_bytes(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: float = 30.0,
    data: bytes | None = None,
) -> bytes:
    """Download an https URL (POST ``data`` if given) and return the response body.

    Raises:
        ValueError: if the URL scheme is not https.
    """
    if urlparse(url).scheme != _HTTPS:
        msg = f"only https URLs are allowed: {url}"
        raise ValueError(msg)
    response = _opener(headers)(url, data, timeout=timeout)
    try:
        return response.read()
    finally:
        response.close()


def fetch_json(url: str, timeout: float = 30.0) -> Json:
    """Download an https URL and parse the body as JSON.

    Raises:
        ValueError: if the URL scheme is not https or the body is not valid JSON.
    """
    return parse_json(fetch_bytes(url, timeout=timeout))
