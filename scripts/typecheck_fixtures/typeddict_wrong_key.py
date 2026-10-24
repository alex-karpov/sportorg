# BUG: access of a key not declared in the TypedDict; checker should report
from typing import TypedDict


class Movie(TypedDict):
    title: str
    year: int


def get(m: Movie) -> str:
    return m["director"]
