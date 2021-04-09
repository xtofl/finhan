from dataclasses import dataclass
from typing import TypeVar, Tuple, Generic

Splittable = TypeVar("Splittable")


def split(t: Splittable) -> Tuple[Splittable]:
    # I would have liked to write map(T.split, text.splitlines())
    # but T is not 'bound' like in C++ generics, so it does not
    # refer to the actual argument of this class.
    return t.split()


@dataclass
class FuzzySearch(Generic[Splittable]):
    def __init__(self, text: Splittable):
        self._text = text

        self._chunks: Tuple[Tuple[Splittable]] = tuple(
            map(split, text.splitlines())
        )

    def __contains__(self, item: Splittable) -> bool:
        return any(
            all(i in chunks for i in item.split()) for chunks in self._chunks
        )

    def __repr__(self):
        return str(self._chunks)
