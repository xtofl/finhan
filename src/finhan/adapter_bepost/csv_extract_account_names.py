#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from functools import partial, reduce
from pathlib import Path
from typing import Iterable, Dict, Tuple

import yaml

from finhan.account import AccountId
from finhan.adapter_bepost.csv_transactions import (
    BePostRow,
    BePostTransactionType,
    extractor,
    bepost_rows,
)


def account_names(
    transactions: Iterable[BePostRow],
) -> Iterable[Tuple[AccountId, str]]:
    it = iter(transactions)
    next(it)  # skip line containing source account id
    header_row = next(it)

    target = extractor(str, header_row.index_of("Rekening tegenpartij :"))
    name = extractor(str, header_row.index_of("Naam tegenpartij"))

    is_regular = BePostRow.transaction_type_is(BePostTransactionType.REGULAR)
    regular_rows = filter(is_regular, it)

    def extract(b: BePostRow):
        return target(b), name(b)

    return set(map(extract, regular_rows))


def from_file(filename: Path) -> Iterable[Tuple[AccountId, str]]:
    with filename.open() as f:
        return account_names(bepost_rows(f.readlines()))


def from_files(csv_files: Iterable[Path]) -> Iterable[Tuple[AccountId, str]]:
    return reduce(set.union, map(set, map(from_file, csv_files)), set())


def main():
    parser = ArgumentParser("Extract account names from csv files")
    parser.add_argument("csv_files", type=str, nargs="*")

    options = parser.parse_args()
    acc = from_files(map(Path, options.csv_files))
    print(f"# generated with {__file__}")
    yaml.safe_dump(
        {
            "schema": "v1",
            "accounts": tuple(
                {"id": k, "name": v} for k, v in acc if any(v.strip())
            ),
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
