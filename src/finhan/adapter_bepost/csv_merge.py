#!/usr/bin/env python3
import sys
from contextlib import contextmanager
from itertools import groupby, chain, starmap
from pathlib import Path
from typing import Iterable, Sequence, Tuple


class Mapping:
    def __init__(self, target: Path, sources: Iterable[Path]):
        self.target = target.name + ".csv"
        self.sources = tuple(sources)

    class OpenMapping:
        def __init__(self, mapping: "Mapping"):
            self.mapping = mapping

        def __enter__(self):
            self.target = open(self.mapping.target, "w")
            self.sources = tuple(map(open, self.mapping.sources))
            return self

        def apply(self):
            first_lines_from_sources = tuple(
                map(lambda f: [f.readline(), f.readline()], self.sources)
            )
            self.target.writelines(first_lines_from_sources[0])
            lines_from_sources = tuple(
                map(
                    lambda f: map(lambda s: s.partition(";")[2], f.readlines()),
                    self.sources,
                )
            )
            lines = set(chain(*lines_from_sources))
            lines = sorted(lines, key=lambda line: line.split(";")[0])
            self.target.writelines(
                starmap(
                    (lambda i, line: ";".join([str(i)] + line.split(";"))),
                    enumerate(lines),
                )
            )

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.target.__exit__(exc_type, exc_val, exc_tb)
            for s in self.sources:
                s.__exit__(exc_type, exc_val, exc_tb)

    @contextmanager
    def open(self):
        with Mapping.OpenMapping(self) as o:
            yield o


def target_files(paths: Iterable[Path]) -> Iterable[Mapping]:
    for a, fs in groupby(iter(paths), key=lambda path: str(path).partition("EURd")[0]):
        yield Mapping(Path(a), fs)


def cooked(paths: Iterable[Path]):
    for mapping in target_files(paths):
        with mapping.open() as open_mapping:
            open_mapping.apply()
        yield mapping.target


def main():
    print(tuple(cooked(map(Path, tuple(sys.argv[1:])))))


if __name__ == "__main__":
    main()
