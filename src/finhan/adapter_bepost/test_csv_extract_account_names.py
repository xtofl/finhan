from .csv_extract_account_names import account_names
from .csv_transactions import bepost_rows


def test_account_names_are_retrieved_from_bepost_transactions(sample: str):
    names = account_names(bepost_rows(sample.splitlines()))
    assert set(names) == set(
        {
            "BE654987654321": "ANOTHER PARTY",
            "BE11405050461148": "Party 1",
            "BE494979796464": "Party 3",
            "BE44664466446": "Party 4",
        }.items()
    )
