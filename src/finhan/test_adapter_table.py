from datetime import datetime

from finhan.adapter_table import generate_from
from finhan.transaction import Transaction


def test_a_table_can_be_generated():
    transactions = (
        Transaction(
            date=datetime(year=2020, month=1, day=5),
            amount=-1000,
            source="BE123456789",
            target="BE987987654",
            message="just for fun",
        ),
        Transaction(
            date=datetime(year=2020, month=5, day=15),
            amount=1000,
            source="BE123456789",
            target="BE987987654",
            message="payback",
        ),
        Transaction(
            date=datetime(year=2020, month=5, day=15),
            amount=10,
            source="BE123456789",
            target="BE987987654",
            message="a little more",
        ),
    )
    party_names = {
        "BE987987654": "party 1",
    }
    assert (
        generate_from(
            "From BE123456789", transactions, account_names=party_names
        )
        == "From BE123456789\n"
        '2020/01/05   -1000.00 BE987987654 "party 1" "just for fun"\n'
        '2020/05/15    1000.00 BE987987654 "party 1" "payback"\n'
        '2020/05/15      10.00 BE987987654 "party 1" "a little more"'
    )
