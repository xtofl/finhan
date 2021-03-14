from datetime import datetime

import pytest

from finhan.account import apply_balance, joint_account_transactions, Account, \
    read_balance
from finhan.adapters.bepost import Transaction


def test_balance_series_ends_in_current_balance():
    numbers = (1, 2, 3, 4)
    balance = tuple(apply_balance(100, numbers))
    assert balance[-1] == 100
    assert balance == (91, 93, 96, 100)


def test_grand_total_ends_in_grand_balance():
    d1 = datetime(year=2021, month=2, day=1)
    d2 = datetime(year=2021, month=2, day=2)
    d3 = datetime(year=2021, month=5, day=3)

    transactions = {
        "A": (
            Transaction(source="A", target="X", amount=100, date=d1),
            Transaction(source="A", target="B", amount=10, date=d1),
            Transaction(source="A", target="B", amount=-10, date=d2),
            Transaction(source="A", target="Y", amount=-50, date=d3),
        ),
        "B": (
            Transaction(source="B", target="A", amount=-10, date=d1),
            Transaction(source="B", target="A", amount=10, date=d2),
        ),
    }
    balances = {"A": Account("A", 1010, ""), "B": Account("B", -10, "")}

    dates, numbers = joint_account_transactions(balances, transactions)
    assert tuple(dates) == (d1, d2, d3)
    assert numbers[-1] == 1000
    assert tuple(numbers) == (1050, 1050, 1000)


def test_balance_can_be_read(tmp_path):
    yaml = r"""
schema: "v1"
last updated: 2021-03-13
accounts:
        -
                id: BE123456789
                name: daily
                balance: 201.11
        -
                id: BE654987321
                name: backup
                balance: 1735.91
        -
                id: BE489156489
                name: savings
                balance: 9134.68
"""
    balance_file = tmp_path / 'b.yml'
    with open(balance_file, 'w') as f:
        f.write(yaml)

    balance = read_balance(balance_file)
    assert set(('BE123456789', 'BE654987321', 'BE489156489')) == set(
        balance.keys())

    assert balance['BE123456789'].name == 'daily'
    assert balance['BE123456789'].balance == 201.11


def test_read_balance_raises_for_unknown_schema(tmp_path):
    yaml = r"""
    schema: "vWHAT?"
    last updated: 2021-03-13
"""
    balance_file = tmp_path / 'b.yml'
    with open(balance_file, 'w') as f:
        f.write(yaml)

    with pytest.raises(Exception):
        read_balance(balance_file)
