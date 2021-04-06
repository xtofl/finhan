import subprocess
from pathlib import Path
from typing import Iterable

import pytest

from tests_e2e.fuzzy_search import FuzzySearch


@pytest.fixture
def raw_data_dir():
    return Path(__file__).parent


@pytest.fixture
def raw_data_files(raw_data_dir):
    return tuple(
        f
        for f in (Path(__file__).parent / "demo-data/obfuscated").iterdir()
        if f.suffix == ".csv"
    )


def test_create_table(raw_data_files: Iterable[Path]):
    table = subprocess.check_output(
        [
            "finhan-table",
            "--account",
            "BE000000200844",
            *map(str, raw_data_files),
        ]
    )
    assert table is not None
    table = FuzzySearch(table)
    assert (
        b'2020/09/15     247.89 BE000000334023 "OVERDRACHT SPAARREKENING "'
        in table
    )
