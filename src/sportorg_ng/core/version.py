"""Smallest real code path so that every quality check has something to run on."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

PARTS = 3


@dataclass(frozen=True, slots=True)
class Version:
    """Semantic version triple."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> Version:
        parts = text.strip().split(".")
        if len(parts) != PARTS:
            msg = f"expected MAJOR.MINOR.PATCH, got {text!r}"
            raise ValueError(msg)
        major, minor, patch = (int(p) for p in parts)
        if min(major, minor, patch) < 0:
            msg = f"version parts must be non-negative, got {text!r}"
            raise ValueError(msg)
        return cls(major, minor, patch)

    @override
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
